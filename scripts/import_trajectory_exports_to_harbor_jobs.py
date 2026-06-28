#!/usr/bin/env python3
"""Import trajectory export JSONL archives into Harbor-shaped job paths.

The exports under ``harbor_benchmark/trajectory_exports`` are containers:
each row has trial metadata plus an embedded ``trajectory`` object.  Some
embedded trajectories are preserved Harbor ``agent/trajectory.json`` files;
others were produced by lightweight converters from raw agent logs.  This
script keeps that distinction explicit while placing available trajectories at:

    harbor_jobs/<source_job>/<trial>/agent/trajectory.json

With ``--write-metadata`` it also writes Harbor-viewer-compatible
``config.json`` / ``result.json`` files at both the job root and trial level.
Those metadata files are explicit reconstructions from the export rows; timing,
token, and cost fields that are not present in the exports remain null.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import re
import uuid
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_EXPORTS_DIR = ROOT / "harbor_benchmark/trajectory_exports/v4_withtest219_20260627"
DEFAULT_JOBS_DIR = ROOT / "harbor_jobs"
TASKS_DIR = ROOT / "harbor_benchmark/tasks_v4"

AGENT_NAMES = {
    "codex": "codex",
    "copilot_cli": "copilot-cli",
    "opencode": "opencode",
    "claude_code": "claude-code",
}


@dataclass(frozen=True)
class RowStatus:
    source: str
    reason: str = ""


def load_jsonl_gz(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, start=1):
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_no}: invalid JSON: {exc}") from exc
    return rows


def classify_trajectory(row: dict[str, Any]) -> RowStatus:
    trajectory = row.get("trajectory")
    source = row.get("trajectory_source") or "missing"
    if trajectory is None:
        return RowStatus(source="missing", reason="row has no embedded trajectory")
    if not isinstance(trajectory, dict):
        return RowStatus(source="bad_shape", reason="trajectory is not an object")
    if not isinstance(trajectory.get("schema_version"), str):
        return RowStatus(source="bad_shape", reason="trajectory.schema_version is missing")
    if not isinstance(trajectory.get("steps"), list):
        return RowStatus(source="bad_shape", reason="trajectory.steps is not a list")
    if source == "existing":
        return RowStatus(source="existing")
    if source == "converted":
        return RowStatus(
            source="converted",
            reason=(
                "lightweight converter output from scripts/"
                "export_llm_harness_trajectories.py"
            ),
        )
    return RowStatus(source=f"unknown:{source}", reason="unrecognized trajectory_source")


def destination_for(row: dict[str, Any], jobs_dir: Path) -> Path:
    source_job = row.get("source_job")
    trial = row.get("trial")
    if not source_job or not trial:
        raise ValueError(f"row is missing source_job/trial: {row!r}")
    return jobs_dir / source_job / trial / "agent" / "trajectory.json"


def write_json(path: Path, value: Any, *, overwrite: bool) -> bool:
    if path.exists() and not overwrite:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")
    return True


def stable_uuid(*parts: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_URL, ":".join(("depbench", *parts))))


def naive_iso_timestamp(value: str | None = None) -> str:
    """Return a Harbor-viewer-friendly naive ISO timestamp.

    Harbor viewer sorts job summaries using parsed datetimes. Mixing
    offset-aware strings (``+00:00``/``Z``) with older naive Harbor result
    timestamps can raise ``TypeError: can't compare offset-naive and
    offset-aware datetimes``.  The original Harbor job roots in this repo use
    naive ISO strings, so reconstructed metadata follows that convention.
    """
    if value:
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
            if parsed.tzinfo is not None:
                parsed = parsed.astimezone(timezone.utc).replace(tzinfo=None)
            return parsed.isoformat()
        except ValueError:
            pass
    return datetime.now(timezone.utc).replace(tzinfo=None).isoformat()


def generated_at_for(exports_dir: Path) -> str:
    index_path = exports_dir / "index.json"
    if index_path.exists():
        try:
            generated_at = json.loads(index_path.read_text()).get("generated_at")
            if isinstance(generated_at, str) and generated_at:
                return naive_iso_timestamp(generated_at)
        except json.JSONDecodeError:
            pass
    return naive_iso_timestamp()


def parse_concurrency(job_name: str) -> int:
    match = re.search(r"conc(\d+)", job_name)
    if match:
        return int(match.group(1))
    return 1


def agent_name(harness: str | None) -> str:
    return AGENT_NAMES.get(harness or "", harness or "unknown")


def task_path(task: str) -> str:
    return f"harbor_benchmark/tasks_v4/{task}"


def task_checksum(task: str, cache: dict[str, str]) -> str:
    if task in cache:
        return cache[task]
    root = TASKS_DIR / task
    digest = hashlib.sha256()
    if not root.exists():
        value = f"missing:{task}"
        cache[task] = value
        return value
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        rel = path.relative_to(root).as_posix()
        digest.update(rel.encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    value = digest.hexdigest()
    cache[task] = value
    return value


def base_agent_config(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": agent_name(row.get("harness")),
        "import_path": None,
        "model_name": row.get("model"),
        "skills": [],
        "override_timeout_sec": None,
        "override_setup_timeout_sec": None,
        "max_timeout_sec": None,
        "extra_allowed_hosts": [],
        "kwargs": {},
        "env": {},
        "mcp_servers": [],
    }


def base_environment_config() -> dict[str, Any]:
    return {
        "type": "docker",
        "import_path": None,
        "force_build": False,
        "delete": True,
        "cpu_enforcement_policy": "auto",
        "memory_enforcement_policy": "auto",
        "override_cpus": None,
        "override_memory_mb": 8192,
        "override_storage_mb": None,
        "override_gpus": None,
        "override_tpu": None,
        "mounts": None,
        "extra_docker_compose": [],
        "env": {},
        "kwargs": {},
        "extra_allowed_hosts": [],
    }


def base_verifier_config() -> dict[str, Any]:
    return {
        "override_timeout_sec": None,
        "max_timeout_sec": None,
        "env": {},
        "disable": False,
    }


def trial_config_for(
    row: dict[str, Any],
    *,
    job_root: Path,
    job_id: str,
) -> dict[str, Any]:
    task = row["task"]
    return {
        "task": {
            "path": task_path(task),
            "git_url": None,
            "git_commit_id": None,
            "name": None,
            "ref": None,
            "overwrite": False,
            "download_dir": None,
            "source": "tasks_v4",
        },
        "trial_name": row["trial"],
        "trials_dir": str(job_root.relative_to(ROOT)),
        "timeout_multiplier": 1.0,
        "agent_timeout_multiplier": None,
        "verifier_timeout_multiplier": None,
        "agent_setup_timeout_multiplier": None,
        "environment_build_timeout_multiplier": None,
        "agent": base_agent_config(row),
        "environment": base_environment_config(),
        "verifier": base_verifier_config(),
        "artifacts": [],
        "extra_instruction_paths": [],
        "job_id": job_id,
    }


def exception_info_for(row: dict[str, Any], generated_at: str) -> dict[str, Any] | None:
    exception_type = row.get("exception_type")
    if not exception_type:
        return None
    return {
        "exception_type": exception_type,
        "exception_message": (
            "Recovered from trajectory export metadata; original exception "
            "message/traceback is unavailable in this compact export."
        ),
        "exception_traceback": "",
        "occurred_at": generated_at,
    }


def trial_result_for(
    row: dict[str, Any],
    *,
    job_root: Path,
    trial_root: Path,
    job_id: str,
    generated_at: str,
    checksum_cache: dict[str, str],
) -> dict[str, Any]:
    config = trial_config_for(row, job_root=job_root, job_id=job_id)
    reward = row.get("reward")
    verifier_result = None
    if reward is not None:
        verifier_result = {"rewards": {"reward": float(reward)}}
    return {
        "id": stable_uuid("trial", row["source_job"], row["trial"]),
        "task_name": f"depbot/{row['task']}",
        "trial_name": row["trial"],
        "trial_uri": trial_root.resolve().as_uri(),
        "task_id": {"path": task_path(row["task"])},
        "source": "tasks_v4",
        "task_checksum": task_checksum(row["task"], checksum_cache),
        "config": config,
        "agent_info": {
            "name": agent_name(row.get("harness")),
            "version": "unknown",
            "model_info": {
                "name": row.get("model"),
                "provider": None,
            },
        },
        "agent_result": {
            "n_input_tokens": None,
            "n_cache_tokens": None,
            "n_output_tokens": None,
            "cost_usd": None,
            "rollout_details": None,
            "metadata": {
                "llm": row.get("llm"),
                "harness": row.get("harness"),
                "trajectory_source": row.get("trajectory_source"),
                "has_trajectory": row.get("has_trajectory"),
                "source_job": row.get("source_job"),
                "source_trial_path": row.get("source_trial_path"),
                "raw_log_path": row.get("raw_log_path"),
            },
        },
        "verifier_result": verifier_result,
        "exception_info": exception_info_for(row, generated_at),
        "started_at": generated_at,
        "finished_at": generated_at,
        "environment_setup": None,
        "agent_setup": None,
        "agent_execution": None,
        "verifier": None,
        "step_results": None,
    }


def job_config_for(job_name: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    first = rows[0]
    task_names = [row["task"] for row in rows]
    return {
        "job_name": job_name,
        "jobs_dir": "harbor_jobs",
        "n_attempts": 1,
        "timeout_multiplier": 1.0,
        "agent_timeout_multiplier": None,
        "verifier_timeout_multiplier": None,
        "agent_setup_timeout_multiplier": None,
        "environment_build_timeout_multiplier": None,
        "debug": False,
        "n_concurrent_trials": parse_concurrency(job_name),
        "quiet": False,
        "retry": {
            "max_retries": 0,
            "include_exceptions": None,
            "exclude_exceptions": [
                "VerifierTimeoutError",
                "RewardFileNotFoundError",
                "AgentTimeoutError",
                "VerifierOutputParseError",
                "RewardFileEmptyError",
            ],
            "wait_multiplier": 1.0,
            "min_wait_sec": 1.0,
            "max_wait_sec": 60.0,
        },
        "environment": base_environment_config(),
        "verifier": base_verifier_config(),
        "metrics": [],
        "agents": [base_agent_config(first)],
        "datasets": [
            {
                "path": "harbor_benchmark/tasks_v4",
                "name": None,
                "version": None,
                "ref": None,
                "registry_url": None,
                "registry_path": None,
                "repo": None,
                "overwrite": False,
                "download_dir": None,
                "task_names": task_names,
                "exclude_task_names": None,
                "n_tasks": None,
            }
        ],
        "tasks": [],
        "artifacts": [],
        "extra_instruction_paths": [],
        "plugins": [],
    }


def job_result_for(
    job_name: str,
    rows: list[dict[str, Any]],
    *,
    generated_at: str,
) -> dict[str, Any]:
    first = rows[0]
    reward_stats: dict[str, dict[str, list[str]]] = {"reward": {}}
    exception_stats: dict[str, list[str]] = defaultdict(list)
    n_reward = 0
    for row in rows:
        reward = row.get("reward")
        if reward is not None:
            n_reward += 1
            reward_key = f"{float(reward):.1f}"
            reward_stats["reward"].setdefault(reward_key, []).append(row["trial"])
        if row.get("exception_type"):
            exception_stats[row["exception_type"]].append(row["trial"])

    pass_count = len(reward_stats["reward"].get("1.0", []))
    mean = pass_count / n_reward if n_reward else 0.0
    eval_key = f"{agent_name(first.get('harness'))}__{first.get('model')}__tasks_v4"
    return {
        "id": stable_uuid("job", job_name),
        "started_at": generated_at,
        "updated_at": generated_at,
        "finished_at": generated_at,
        "n_total_trials": len(rows),
        "stats": {
            "n_completed_trials": n_reward,
            "n_errored_trials": len(rows) - n_reward,
            "n_running_trials": 0,
            "n_pending_trials": 0,
            "n_cancelled_trials": 0,
            "n_retries": 0,
            "evals": {
                eval_key: {
                    "n_trials": len(rows),
                    "n_errors": len(rows) - n_reward,
                    "metrics": [{"mean": mean}],
                    "pass_at_k": {},
                    "reward_stats": reward_stats,
                    "exception_stats": dict(exception_stats),
                }
            },
            "n_input_tokens": None,
            "n_cache_tokens": None,
            "n_output_tokens": None,
            "cost_usd": None,
            "reconstructed_from": {
                "trajectory_exports": "harbor_benchmark/trajectory_exports/v4_withtest219_20260627",
                "note": (
                    "Root result reconstructed from compact trajectory export rows; "
                    "timing/token/cost fields were not present in the export."
                ),
            },
        },
    }


def import_exports(
    exports_dir: Path,
    jobs_dir: Path,
    *,
    write: bool,
    write_metadata: bool,
    overwrite: bool,
) -> dict[str, Any]:
    summary: dict[str, Any] = {
        "exports_dir": str(exports_dir),
        "jobs_dir": str(jobs_dir),
        "write": write,
        "write_metadata": write_metadata,
        "overwrite": overwrite,
        "files": [],
        "totals": Counter(),
        "jobs": defaultdict(Counter),
    }
    generated_at = generated_at_for(exports_dir)
    checksum_cache: dict[str, str] = {}

    for export_file in sorted(exports_dir.glob("*.jsonl.gz")):
        rows = load_jsonl_gz(export_file)
        counts: Counter[str] = Counter()
        wrote = skipped_existing = 0
        metadata_wrote = metadata_skipped = 0
        examples: dict[str, dict[str, str | None]] = {}
        rows_by_job: dict[str, list[dict[str, Any]]] = defaultdict(list)

        for row in rows:
            status = classify_trajectory(row)
            counts[status.source] += 1
            summary["totals"][status.source] += 1
            if row.get("source_job"):
                summary["jobs"][row["source_job"]][status.source] += 1
                rows_by_job[row["source_job"]].append(row)
            examples.setdefault(
                status.source,
                {
                    "task": row.get("task"),
                    "trial": row.get("trial"),
                    "reason": status.reason or None,
                },
            )

            trajectory_path = destination_for(row, jobs_dir)
            if status.source in {"existing", "converted"}:
                if write:
                    did_write = write_json(
                        trajectory_path,
                        row["trajectory"],
                        overwrite=overwrite,
                    )
                    if did_write:
                        wrote += 1
                    else:
                        skipped_existing += 1

            if write and write_metadata:
                # Metadata is useful even for rows with missing trajectories.
                trial_root = trajectory_path.parents[1]
                job_root = trial_root.parent
                job_id = stable_uuid("job", row["source_job"])
                config = trial_config_for(row, job_root=job_root, job_id=job_id)
                result = trial_result_for(
                    row,
                    job_root=job_root,
                    trial_root=trial_root,
                    job_id=job_id,
                    generated_at=generated_at,
                    checksum_cache=checksum_cache,
                )
                wrote_config = write_json(
                    trial_root / "config.json",
                    config,
                    overwrite=overwrite,
                )
                wrote_result = write_json(
                    trial_root / "result.json",
                    result,
                    overwrite=overwrite,
                )
                if wrote_config or wrote_result:
                    metadata_wrote += int(wrote_config) + int(wrote_result)
                else:
                    metadata_skipped += 2

        if write and write_metadata:
            for source_job, job_rows in rows_by_job.items():
                job_root = jobs_dir / source_job
                wrote_config = write_json(
                    job_root / "config.json",
                    job_config_for(source_job, job_rows),
                    overwrite=overwrite,
                )
                wrote_result = write_json(
                    job_root / "result.json",
                    job_result_for(source_job, job_rows, generated_at=generated_at),
                    overwrite=overwrite,
                )
                if wrote_config or wrote_result:
                    metadata_wrote += int(wrote_config) + int(wrote_result)
                else:
                    metadata_skipped += 2

        summary["files"].append(
            {
                "file": str(export_file.relative_to(ROOT)),
                "rows": len(rows),
                "counts": dict(counts),
                "wrote": wrote,
                "skipped_existing": skipped_existing,
                "metadata_wrote": metadata_wrote,
                "metadata_skipped": metadata_skipped,
                "examples": examples,
            }
        )

    summary["totals"] = dict(summary["totals"])
    summary["jobs"] = {job: dict(counter) for job, counter in summary["jobs"].items()}
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--exports-dir", type=Path, default=DEFAULT_EXPORTS_DIR)
    parser.add_argument("--jobs-dir", type=Path, default=DEFAULT_JOBS_DIR)
    parser.add_argument("--write", action="store_true", help="write files under harbor_jobs")
    parser.add_argument(
        "--write-metadata",
        action="store_true",
        help="write Harbor-shaped config.json/result.json files",
    )
    parser.add_argument("--overwrite", action="store_true", help="replace existing imports")
    args = parser.parse_args()

    summary = import_exports(
        args.exports_dir.resolve(),
        args.jobs_dir.resolve(),
        write=args.write,
        write_metadata=args.write_metadata,
        overwrite=args.overwrite,
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
