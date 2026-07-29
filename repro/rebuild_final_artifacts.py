#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""Align released outcomes, trajectories, and verifier logs to final trials."""

from __future__ import annotations

import argparse
import csv
import gzip
import json
import shutil
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from trajectory_conversion import trajectory_from_trial


ROOT = Path(__file__).resolve().parents[1]
ORIGINAL_RESULTS = ROOT / "results/original_per_trial_results.jsonl.gz"
FINAL_RESULTS = ROOT / "results/per_trial_results.jsonl.gz"
TARGETED_RESULTS = ROOT / "results/targeted_runtime_exception_reruns_203.csv"
RECOVERY_RESULTS = ROOT / "results/trajectory_recovery_reruns_203.csv"
CORRECTION_RESULTS = (
    ROOT / "results/task_metadata_correction_reruns_203.csv"
)
AFFECTED_RESULTS = ROOT / "results/affected_contract_reruns_203.csv"
ENVIRONMENT_RESULTS = ROOT / "results/environment_repair_reruns_203.csv"

TARGETED_CONFIGURATIONS = {
    "codex_gpt55": ("gpt55__codex", "codex", "gpt55", "gpt-5.5"),
    "copilot_gemini": (
        "gemini35flash__copilot_cli",
        "copilot_cli",
        "gemini35flash",
        "gemini-3.5-flash",
    ),
    "copilot_gpt55": (
        "gpt55__copilot_cli",
        "copilot_cli",
        "gpt55",
        "gpt-5.5",
    ),
    "opencode_gpt55": (
        "gpt55__opencode",
        "opencode",
        "gpt55",
        "gpt-5.5",
    ),
}

CONFIGURATIONS = {
    "claude48__claude_code": (
        "claude_code",
        "claude48",
        "claude-opus-4-8",
    ),
    "claude48__copilot_cli": (
        "copilot_cli",
        "claude48",
        "claude-opus-4-8",
    ),
    "claude48__opencode": (
        "opencode",
        "claude48",
        "claude-opus-4-8",
    ),
    "gemini35flash__claude_code": (
        "claude_code",
        "gemini35flash",
        "gemini-3.5-flash",
    ),
    "gemini35flash__copilot_cli": (
        "copilot_cli",
        "gemini35flash",
        "gemini-3.5-flash",
    ),
    "gemini35flash__opencode": (
        "opencode",
        "gemini35flash",
        "gemini-3.5-flash",
    ),
    "gpt55__claude_code": ("claude_code", "gpt55", "gpt-5.5"),
    "gpt55__codex": ("codex", "gpt55", "gpt-5.5"),
    "gpt55__copilot_cli": ("copilot_cli", "gpt55", "gpt-5.5"),
    "gpt55__opencode": ("opencode", "gpt55", "gpt-5.5"),
}


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    with gzip.open(path, "wt", encoding="utf-8") as handle:
        for row in rows:
            handle.write(
                json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n"
            )


def normalize_task(result: dict[str, Any]) -> str:
    task_name = result.get("task_name") or ""
    return task_name.split("/")[-1]


def clean_message(value: Any) -> str:
    return "\n".join(
        line.rstrip() for line in str(value or "").splitlines()
    ).strip()


def reward_from_result(result: dict[str, Any]) -> float | None:
    reward = (
        ((result.get("verifier_result") or {}).get("rewards") or {}).get(
            "reward"
        )
    )
    if reward is None:
        return None
    return float(reward)


def exception_from_result(result: dict[str, Any]) -> tuple[str, str]:
    exception = result.get("exception_info") or {}
    message = clean_message(
        exception.get("exception_message") or exception.get("message")
    )
    return (
        exception.get("exception_type") or exception.get("type") or "",
        message,
    )


def load_trial_replacement(
    *,
    stem: str,
    harness: str,
    llm: str,
    model: str,
    task: str,
    source: str,
    job_name: str,
    trial_name: str,
    trial_dir: Path,
    expected_reward: float | None = None,
    allow_timeout_as_zero: bool = False,
) -> dict[str, Any]:
    result_path = trial_dir / "result.json"
    if not result_path.exists():
        raise SystemExit(f"missing rerun result: {result_path}")
    result = json.loads(result_path.read_text(encoding="utf-8"))
    observed_task = normalize_task(result)
    if observed_task != task:
        raise SystemExit(
            f"{trial_dir}: expected task {task}, observed {observed_task}"
        )

    reward = reward_from_result(result)
    exception_type, exception_message = exception_from_result(result)
    if (
        allow_timeout_as_zero
        and reward is None
        and expected_reward == 0.0
        and exception_type == "AgentTimeoutError"
    ):
        reward = 0.0
    if expected_reward is not None and reward != expected_reward:
        raise SystemExit(
            f"{stem}/{task}: CSV reward {expected_reward} != trial reward {reward}"
        )
    trajectory, trajectory_source = trajectory_from_trial(
        trial_dir, harness=harness, model=model
    )
    if trajectory is None:
        raise SystemExit(f"{stem}/{task}: no recoverable final trajectory")

    return {
        "configuration": stem,
        "harness": harness,
        "llm": llm,
        "model": model,
        "task": task,
        "reward": reward,
        "exception_type": exception_type,
        "exception_message": exception_message,
        "outcome_source": source,
        "source_job": job_name,
        "trial": trial_name,
        "trial_dir": trial_dir,
        "trajectory": trajectory,
        "trajectory_source": trajectory_source,
        "started_at": result.get("started_at") or "",
        "finished_at": result.get("finished_at") or "",
    }


def load_targeted_replacements(
    experiment_root: Path,
) -> dict[tuple[str, str], dict[str, Any]]:
    replacements: dict[tuple[str, str], dict[str, Any]] = {}
    rows = list(csv.DictReader(TARGETED_RESULTS.open(encoding="utf-8")))
    for row in rows:
        stem, harness, llm, model = TARGETED_CONFIGURATIONS[
            row["configuration"]
        ]
        trial_dir = (
            experiment_root
            / "harbor_jobs"
            / row["job_name"]
            / row["trial"]
        )
        replacement = load_trial_replacement(
            stem=stem,
            harness=harness,
            llm=llm,
            model=model,
            task=row["task"],
            source="targeted_rerun",
            job_name=row["job_name"],
            trial_name=row["trial"],
            trial_dir=trial_dir,
            expected_reward=float(row["reward"]),
        )
        key = (stem, row["task"])
        if key in replacements:
            raise SystemExit(f"duplicate targeted replacement: {key}")
        replacements[key] = replacement
    if len(replacements) != 111:
        raise SystemExit(
            f"expected 111 targeted replacements, got {len(replacements)}"
        )
    return replacements


def load_recovery_replacements(
    experiment_root: Path,
) -> dict[tuple[str, str], dict[str, Any]]:
    manifest_path = (
        experiment_root
        / "_run_configs/trajectory_recovery_20260723/manifest.json"
    )
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    replacements: dict[tuple[str, str], dict[str, Any]] = {}

    for llm, group in manifest["groups"].items():
        stem = f"{llm}__opencode"
        model = group["model"]
        for job in group["jobs"]:
            job_dir = experiment_root / "harbor_jobs" / job["job_name"]
            if not job_dir.is_dir():
                raise SystemExit(f"recovery job is missing: {job_dir}")

            trials: dict[str, Path] = {}
            for result_path in job_dir.glob("*/result.json"):
                result = json.loads(result_path.read_text(encoding="utf-8"))
                task = normalize_task(result)
                if task:
                    trials[task] = result_path.parent

            expected_tasks = set(job["tasks"])
            missing_tasks = expected_tasks - set(trials)
            if missing_tasks:
                raise SystemExit(
                    f"{job['job_name']}: missing expected tasks "
                    f"{sorted(missing_tasks)}"
                )

            for task in job["tasks"]:
                trial_dir = trials[task]
                replacement = load_trial_replacement(
                    stem=stem,
                    harness="opencode",
                    llm=llm,
                    model=model,
                    task=task,
                    source="trajectory_recovery_rerun",
                    job_name=job["job_name"],
                    trial_name=trial_dir.name,
                    trial_dir=trial_dir,
                )
                key = (stem, task)
                if key in replacements:
                    raise SystemExit(f"duplicate recovery replacement: {key}")
                replacements[key] = replacement

    expected = sum(
        group["missing_tasks"] for group in manifest["groups"].values()
    )
    if len(replacements) != expected or expected != 177:
        raise SystemExit(
            f"expected 177 recovery replacements, got {len(replacements)}"
        )
    return replacements


def load_correction_replacements(
    experiment_root: Path,
) -> dict[tuple[str, str], dict[str, Any]]:
    replacements: dict[tuple[str, str], dict[str, Any]] = {}
    rows = list(csv.DictReader(CORRECTION_RESULTS.open(encoding="utf-8")))
    for row in rows:
        stem = row["configuration"]
        harness, llm, model = CONFIGURATIONS[stem]
        trial_dir = (
            experiment_root
            / "harbor_jobs"
            / row["job_name"]
            / row["trial"]
        )
        replacement = load_trial_replacement(
            stem=stem,
            harness=harness,
            llm=llm,
            model=model,
            task=row["task"],
            source="task_metadata_correction_rerun",
            job_name=row["job_name"],
            trial_name=row["trial"],
            trial_dir=trial_dir,
            expected_reward=float(row["reward"]),
        )
        key = (stem, row["task"])
        if key in replacements:
            raise SystemExit(f"duplicate correction replacement: {key}")
        replacements[key] = replacement
    if len(replacements) != 10:
        raise SystemExit(
            f"expected 10 metadata-correction replacements, got "
            f"{len(replacements)}"
        )
    return replacements


def load_affected_replacements(
    rerun_root: Path,
) -> dict[tuple[str, str], dict[str, Any]]:
    replacements: dict[tuple[str, str], dict[str, Any]] = {}
    rows = list(csv.DictReader(AFFECTED_RESULTS.open(encoding="utf-8")))
    for row in rows:
        stem = row["configuration"]
        harness, llm, model = CONFIGURATIONS[stem]
        trial_dir = rerun_root / row["trial_dir"]
        replacement = load_trial_replacement(
            stem=stem,
            harness=harness,
            llm=llm,
            model=model,
            task=row["task"],
            source="affected_contract_rerun",
            job_name=row["job_name"],
            trial_name=row["trial"],
            trial_dir=trial_dir,
            expected_reward=float(row["reward"]),
            allow_timeout_as_zero=True,
        )
        key = (stem, row["task"])
        if key in replacements:
            raise SystemExit(f"duplicate affected rerun replacement: {key}")
        replacements[key] = replacement

    tasks = {task for _, task in replacements}
    configurations = {configuration for configuration, _ in replacements}
    if (
        len(replacements) != 560
        or len(tasks) != 56
        or configurations != set(CONFIGURATIONS)
    ):
        raise SystemExit(
            "expected a complete 56-task x 10-configuration affected rerun, "
            f"got cells={len(replacements)} tasks={len(tasks)} "
            f"configurations={len(configurations)}"
        )
    return replacements


def load_environment_replacements(
    rerun_root: Path,
) -> dict[tuple[str, str], dict[str, Any]]:
    replacements: dict[tuple[str, str], dict[str, Any]] = {}
    rows = list(csv.DictReader(ENVIRONMENT_RESULTS.open(encoding="utf-8")))
    for row in rows:
        stem = row["configuration"]
        harness, llm, model = CONFIGURATIONS[stem]
        trial_dir = rerun_root / row["trial_dir"]
        replacement = load_trial_replacement(
            stem=stem,
            harness=harness,
            llm=llm,
            model=model,
            task=row["task"],
            source="environment_repair_rerun",
            job_name=row["job_name"],
            trial_name=row["trial"],
            trial_dir=trial_dir,
            expected_reward=float(row["reward"]),
            allow_timeout_as_zero=True,
        )
        key = (stem, row["task"])
        if key in replacements:
            raise SystemExit(
                f"duplicate environment rerun replacement: {key}"
            )
        replacements[key] = replacement

    tasks = {task for _, task in replacements}
    configurations = {configuration for configuration, _ in replacements}
    if (
        len(replacements) != 240
        or len(tasks) != 24
        or configurations != set(CONFIGURATIONS)
    ):
        raise SystemExit(
            "expected a complete 24-task x 10-configuration environment "
            f"rerun, got cells={len(replacements)} tasks={len(tasks)} "
            f"configurations={len(configurations)}"
        )
    return replacements


def verifier_row(replacement: dict[str, Any]) -> dict[str, Any]:
    trial_dir = replacement["trial_dir"]
    stdout_path = trial_dir / "verifier/test-stdout.txt"
    ctrf_path = trial_dir / "verifier/ctrf.json"
    reward_path = trial_dir / "verifier/reward.txt"
    ctrf = None
    if ctrf_path.exists() and ctrf_path.stat().st_size:
        try:
            ctrf = json.loads(ctrf_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            ctrf = None
    return {
        "dataset": "DepBench contract-clean 203",
        "harness": replacement["harness"],
        "llm": replacement["llm"],
        "model": replacement["model"],
        "task": replacement["task"],
        "trial": replacement["trial"],
        "reward": replacement["reward"],
        "exception_type": replacement["exception_type"],
        "exception_message": replacement["exception_message"],
        "has_trajectory": True,
        "trajectory_file": f"{replacement['configuration']}.jsonl.gz",
        "outcome_source": replacement["outcome_source"],
        "source_job": replacement["source_job"],
        "verifier_reward_txt": (
            reward_path.read_text(encoding="utf-8", errors="ignore").strip()
            if reward_path.exists()
            else ""
        ),
        "verifier_test_stdout": (
            stdout_path.read_text(encoding="utf-8", errors="ignore")
            if stdout_path.exists()
            else ""
        ),
        "verifier_ctrf": ctrf,
    }


def trajectory_row(replacement: dict[str, Any]) -> dict[str, Any]:
    return {
        "llm": replacement["llm"],
        "harness": replacement["harness"],
        "model": replacement["model"],
        "task": replacement["task"],
        "trial": replacement["trial"],
        "reward": replacement["reward"],
        "exception_type": replacement["exception_type"],
        "exception_message": replacement["exception_message"],
        "outcome_source": replacement["outcome_source"],
        "source_job": replacement["source_job"],
        "trajectory_source": replacement["trajectory_source"],
        "has_trajectory": True,
        "trajectory": replacement["trajectory"],
    }


def merge_artifact_rows(
    replacements: dict[tuple[str, str], dict[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
    merged_trajectories: dict[str, list[dict[str, Any]]] = {}
    merged_verifiers: dict[str, list[dict[str, Any]]] = {}
    matched: set[tuple[str, str]] = set()

    for trajectory_path in sorted((ROOT / "trajectories").glob("*.jsonl.gz")):
        stem = trajectory_path.name.removesuffix(".jsonl.gz")
        verify_path = ROOT / "verify_logs" / trajectory_path.name
        trajectory_rows = read_jsonl(trajectory_path)
        verify_rows = read_jsonl(verify_path)
        verify_by_task = {row["task"]: row for row in verify_rows}
        if len(trajectory_rows) != 203 or len(verify_by_task) != 203:
            raise SystemExit(f"{stem}: expected 203 trajectory/verifier rows")

        new_trajectory_rows = []
        new_verify_rows = []
        for old_trajectory in trajectory_rows:
            task = old_trajectory["task"]
            key = (stem, task)
            replacement = replacements.get(key)
            if replacement:
                new_trajectory_rows.append(trajectory_row(replacement))
                new_verify_rows.append(verifier_row(replacement))
                matched.add(key)
                continue

            old_trajectory.setdefault(
                "outcome_source", "original_full_run"
            )
            old_trajectory.setdefault("source_job", "")
            old_trajectory.setdefault(
                "trajectory_source",
                "release_snapshot" if old_trajectory.get("trajectory") else "missing",
            )
            old_verify = verify_by_task[task]
            old_verify["dataset"] = "DepBench contract-clean 203"
            old_verify.setdefault("outcome_source", "original_full_run")
            old_verify.setdefault("source_job", "")
            new_trajectory_rows.append(old_trajectory)
            new_verify_rows.append(old_verify)

        merged_trajectories[stem] = new_trajectory_rows
        merged_verifiers[stem] = new_verify_rows

    missing = set(replacements) - matched
    if missing:
        raise SystemExit(f"replacement cells not found in release: {sorted(missing)}")

    for stem, rows in merged_trajectories.items():
        write_jsonl(ROOT / "trajectories" / f"{stem}.jsonl.gz", rows)
        write_jsonl(ROOT / "verify_logs" / f"{stem}.jsonl.gz", merged_verifiers[stem])
    return merged_trajectories


def ensure_original_results() -> list[dict[str, Any]]:
    if not ORIGINAL_RESULTS.exists():
        rows = read_jsonl(FINAL_RESULTS)
        if any(row.get("outcome_source") for row in rows):
            raise SystemExit(
                "cannot infer original results from an already merged final export"
            )
        shutil.copyfile(FINAL_RESULTS, ORIGINAL_RESULTS)
    rows = read_jsonl(ORIGINAL_RESULTS)
    if len(rows) != 2030:
        raise SystemExit(f"expected 2030 original result rows, got {len(rows)}")
    return rows


def outcome_rows(
    original_rows: list[dict[str, Any]],
    replacements: dict[tuple[str, str], dict[str, Any]],
) -> list[dict[str, Any]]:
    rows = []
    matched = set()
    for original in original_rows:
        stem = f"{original['llm']}__{original['harness']}"
        key = (stem, original["task"])
        replacement = replacements.get(key)
        final_reward = replacement["reward"] if replacement else original["reward"]
        final_trial = replacement["trial"] if replacement else original["trial"]
        source = (
            replacement["outcome_source"]
            if replacement
            else "original_full_run"
        )
        if replacement:
            matched.add(key)
        rows.append(
            {
                "configuration": stem,
                "harness": original["harness"],
                "llm": original["llm"],
                "model": original["model"],
                "task": original["task"],
                "original_reward": (
                    "" if original["reward"] is None else original["reward"]
                ),
                "final_reward": "" if final_reward is None else final_reward,
                "outcome_source": source,
                "original_trial": original["trial"],
                "final_trial": final_trial,
                "final_job": replacement["source_job"] if replacement else "",
                "final_exception_type": (
                    replacement["exception_type"]
                    if replacement
                    else original.get("exception_type", "")
                ),
                "final_exception_message": (
                    replacement["exception_message"]
                    if replacement
                    else clean_message(original.get("exception_message", ""))
                ),
                "rerun_trial": replacement["trial"] if replacement else "",
                "rerun_exception_type": (
                    replacement["exception_type"] if replacement else ""
                ),
                "rerun_exception_message": (
                    replacement["exception_message"] if replacement else ""
                ),
            }
        )
    if set(replacements) != matched:
        raise SystemExit("final outcomes did not consume every replacement")
    return rows


def write_final_outcomes(rows: list[dict[str, Any]]) -> None:
    path = ROOT / "results/final_per_task_outcomes.csv"
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=list(rows[0]), lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)


def classify_reward(value: Any) -> str:
    if value in (None, ""):
        return "no_reward"
    if float(value) == 1.0:
        return "pass"
    return "fail"


def rate(numerator: int, denominator: int) -> str:
    if denominator == 0:
        return "0"
    return f"{numerator / denominator:.6f}".rstrip("0").rstrip(".")


def summary_for(rows: list[dict[str, Any]]) -> dict[str, Any]:
    counts = Counter(classify_reward(row["final_reward"]) for row in rows)
    tasks = len(rows)
    reward_bearing = tasks - counts["no_reward"]
    return {
        "tasks": tasks,
        "pass": counts["pass"],
        "fail": counts["fail"],
        "no_reward": counts["no_reward"],
        "pass_rate_total": rate(counts["pass"], tasks),
        "pass_rate_reward_bearing": rate(counts["pass"], reward_bearing),
    }


def update_numeric_summaries(
    outcomes: list[dict[str, Any]],
    trajectories: dict[str, list[dict[str, Any]]],
    replacement_counts: Counter,
) -> None:
    by_configuration: dict[str, list[dict[str, Any]]] = {}
    for row in outcomes:
        by_configuration.setdefault(row["configuration"], []).append(row)

    summary_csv_path = ROOT / "results/summary.csv"
    summary_rows = list(
        csv.DictReader(summary_csv_path.open(encoding="utf-8"))
    )
    for row in summary_rows:
        stem = f"{row['llm']}__{row['harness']}"
        values = summary_for(by_configuration[stem])
        trajectory_rows = trajectories[stem]
        row.update({key: str(value) for key, value in values.items()})
        row["trajectory_file"] = f"{stem}.jsonl.gz"
        row["with_trajectory"] = str(
            sum(bool(item.get("trajectory")) for item in trajectory_rows)
        )
        row["missing_trajectory"] = str(
            len(trajectory_rows) - int(row["with_trajectory"])
        )
    with summary_csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=list(summary_rows[0]), lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(summary_rows)

    summary_json_path = ROOT / "results/summary.json"
    document = json.loads(summary_json_path.read_text(encoding="utf-8"))
    csv_by_configuration = {
        row["configuration"]: row for row in summary_rows
    }
    for row in document["configurations"]:
        csv_row = csv_by_configuration[row["configuration"]]
        for field in (
            "tasks",
            "pass",
            "fail",
            "no_reward",
            "with_trajectory",
            "missing_trajectory",
        ):
            row[field] = int(csv_row[field])
        for field in ("pass_rate_total", "pass_rate_reward_bearing"):
            row[field] = float(csv_row[field])
        row["trajectory_file"] = csv_row["trajectory_file"]
    document["dataset"] = "DepBench contract-clean 203"
    document["generated_at"] = datetime.now(timezone.utc).isoformat()
    document["targeted_rerun_cells"] = replacement_counts["targeted_rerun"]
    document["trajectory_recovery_rerun_cells"] = replacement_counts[
        "trajectory_recovery_rerun"
    ]
    document["task_metadata_correction_rerun_cells"] = replacement_counts[
        "task_metadata_correction_rerun"
    ]
    document["affected_contract_rerun_cells"] = replacement_counts[
        "affected_contract_rerun"
    ]
    document["environment_repair_rerun_cells"] = replacement_counts[
        "environment_repair_rerun"
    ]
    document["task_metadata_correction_rerun_results"] = str(
        CORRECTION_RESULTS.relative_to(ROOT)
    )
    document["affected_contract_rerun_results"] = str(
        AFFECTED_RESULTS.relative_to(ROOT)
    )
    document["environment_repair_rerun_results"] = str(
        ENVIRONMENT_RESULTS.relative_to(ROOT)
    )
    summary_json_path.write_text(
        json.dumps(document, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )

    task_summary = json.loads(
        (ROOT / "dataset/task_summary.json").read_text(encoding="utf-8")
    )
    ecosystems = {row["folder"]: row["ecosystem"] for row in task_summary}
    ecosystem_path = ROOT / "analysis/ecosystem_results.csv"
    ecosystem_rows = list(
        csv.DictReader(ecosystem_path.open(encoding="utf-8"))
    )
    model_to_llm = {
        "gpt-5.5": "gpt55",
        "gemini-3.5-flash": "gemini35flash",
        "claude-opus-4-8": "claude48",
    }
    for row in ecosystem_rows:
        stem = f"{model_to_llm[row['model']]}__{row['harness']}"
        subset = [
            item
            for item in by_configuration[stem]
            if ecosystems[item["task"]] == row["ecosystem"]
        ]
        values = summary_for(subset)
        row.update({key: str(value) for key, value in values.items()})
    with ecosystem_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=list(ecosystem_rows[0]), lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(ecosystem_rows)


def group_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    counts = Counter(classify_reward(row.get("reward")) for row in rows)
    return {
        "rows": len(rows),
        "pass": counts["pass"],
        "fail": counts["fail"],
        "no_reward": counts["no_reward"],
    }


def update_indexes(
    trajectories: dict[str, list[dict[str, Any]]],
) -> None:
    trajectory_groups = []
    verifier_groups = []
    coverage_rows = []
    for stem in sorted(trajectories):
        trajectory_rows = trajectories[stem]
        verify_rows = read_jsonl(ROOT / "verify_logs" / f"{stem}.jsonl.gz")
        first = trajectory_rows[0]
        counts = group_counts(trajectory_rows)
        with_trajectory = sum(
            bool(row.get("trajectory")) for row in trajectory_rows
        )
        trajectory_groups.append(
            {
                "llm": first["llm"],
                "harness": first["harness"],
                "model": first["model"],
                "export_file": f"{stem}.jsonl.gz",
                **counts,
                "with_trajectory": with_trajectory,
                "missing": len(trajectory_rows) - with_trajectory,
            }
        )
        verifier_groups.append(
            {
                "harness": first["harness"],
                "llm": first["llm"],
                "model": first["model"],
                "verify_log_file": f"{stem}.jsonl.gz",
                **counts,
                "with_test_stdout": sum(
                    bool(row.get("verifier_test_stdout"))
                    for row in verify_rows
                ),
                "with_ctrf": sum(
                    bool(row.get("verifier_ctrf")) for row in verify_rows
                ),
            }
        )
        coverage_rows.append(
            {
                "configuration": f"{first['harness']} + {first['model']}",
                "harness": first["harness"],
                "model": first["model"],
                "trajectory_file": f"{stem}.jsonl.gz",
                "tasks": len(trajectory_rows),
                "with_trajectory": with_trajectory,
                "missing_trajectory": len(trajectory_rows) - with_trajectory,
                "verify_log_file": f"{stem}.jsonl.gz",
                "with_verifier_stdout": verifier_groups[-1][
                    "with_test_stdout"
                ],
                "with_ctrf": verifier_groups[-1]["with_ctrf"],
            }
        )

    trajectory_fields = [
        "llm",
        "harness",
        "model",
        "export_file",
        "rows",
        "with_trajectory",
        "missing",
        "pass",
        "fail",
        "no_reward",
    ]
    with (ROOT / "trajectories/index.csv").open(
        "w", newline="", encoding="utf-8"
    ) as handle:
        writer = csv.DictWriter(
            handle, fieldnames=trajectory_fields, lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(trajectory_groups)
    (ROOT / "trajectories/index.json").write_text(
        json.dumps(trajectory_groups, indent=2) + "\n", encoding="utf-8"
    )

    verify_fields = [
        "harness",
        "llm",
        "model",
        "verify_log_file",
        "rows",
        "with_test_stdout",
        "with_ctrf",
        "pass",
        "fail",
        "no_reward",
    ]
    with (ROOT / "verify_logs/index.csv").open(
        "w", newline="", encoding="utf-8"
    ) as handle:
        writer = csv.DictWriter(
            handle, fieldnames=verify_fields, lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(verifier_groups)
    (ROOT / "verify_logs/index.json").write_text(
        json.dumps(
            {
                "dataset": "DepBench contract-clean 203",
                "format": (
                    "gzip JSONL; one row per final selected trial, including "
                    "verifier stdout and CTRF JSON when available"
                ),
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "groups": verifier_groups,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    coverage_path = ROOT / "analysis/coverage.csv"
    with coverage_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=list(coverage_rows[0]), lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(coverage_rows)

    lines = [
        "# Trajectory exports",
        "",
        (
            "Each `.jsonl.gz` file contains one JSON object per final selected "
            "task/trial with reward metadata and trajectory JSON when available."
        ),
        "",
        "| LLM | Harness | Rows | With trajectory | Missing trajectory | Export |",
        "|---|---|---:|---:|---:|---|",
    ]
    for row in trajectory_groups:
        lines.append(
            f"| {row['llm']} | {row['harness']} | {row['rows']} | "
            f"{row['with_trajectory']} | {row['missing']} | "
            f"`{row['export_file']}` |"
        )
    lines.extend(
        [
            "",
            (
                "Rows replaced by targeted, trajectory-recovery, task-metadata "
                "correction, affected-contract, or environment-repair reruns "
                "record `outcome_source`, `source_job`, and "
                "`trajectory_source`."
            ),
            "",
            (
                "Release redactions are recorded in "
                "`analysis/release_redactions_2026-07-23.csv`."
            ),
        ]
    )
    (ROOT / "trajectories/README.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )


def write_final_result_export(
    trajectories: dict[str, list[dict[str, Any]]],
) -> None:
    rows = []
    for stem in sorted(trajectories):
        for trajectory in trajectories[stem]:
            rows.append(
                {"dataset": "DepBench contract-clean 203"}
                | {
                    key: value
                    for key, value in trajectory.items()
                    if key not in {"trajectory", "trajectory_source"}
                }
                | {"trajectory_file": f"{stem}.jsonl.gz"}
            )
    write_jsonl(FINAL_RESULTS, rows)


def write_recovery_csv(
    replacements: dict[tuple[str, str], dict[str, Any]],
) -> None:
    rows = [
        {
            "configuration": replacement["configuration"],
            "task": replacement["task"],
            "reward": replacement["reward"],
            "exception_type": replacement["exception_type"],
            "exception_message": replacement["exception_message"],
            "selection": "trajectory-recovery",
            "job_name": replacement["source_job"],
            "trial": replacement["trial"],
            "started_at": replacement["started_at"],
            "finished_at": replacement["finished_at"],
        }
        for replacement in replacements.values()
        if replacement["outcome_source"] == "trajectory_recovery_rerun"
    ]
    rows.sort(key=lambda row: (row["configuration"], row["task"]))
    if not rows:
        return
    with RECOVERY_RESULTS.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=list(rows[0]), lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--experiment-root", type=Path, required=True
    )
    parser.add_argument("--include-recovery", action="store_true")
    parser.add_argument("--include-correction", action="store_true")
    parser.add_argument("--include-affected", action="store_true")
    parser.add_argument("--affected-root", type=Path)
    parser.add_argument("--include-environment", action="store_true")
    parser.add_argument("--environment-root", type=Path)
    args = parser.parse_args()

    experiment_root = args.experiment_root.resolve()
    original_rows = ensure_original_results()
    replacements = load_targeted_replacements(experiment_root)
    recovery_replacements: dict[tuple[str, str], dict[str, Any]] = {}
    if args.include_recovery:
        recovery_replacements = load_recovery_replacements(experiment_root)
        replacements.update(recovery_replacements)
    if args.include_correction:
        correction_replacements = load_correction_replacements(experiment_root)
        expected_overrides = {
            ("gemini35flash__opencode", "strawberry-graphql__strawberry__282"),
            ("gpt55__codex", "strawberry-graphql__strawberry__282"),
            ("gpt55__copilot_cli", "strawberry-graphql__strawberry__282"),
        }
        observed_overrides = set(replacements) & set(correction_replacements)
        if observed_overrides != expected_overrides:
            raise SystemExit(
                "unexpected metadata-correction override cells: "
                f"{sorted(observed_overrides)}"
            )
        replacements.update(correction_replacements)
    if args.include_affected:
        if args.affected_root is None:
            raise SystemExit("--include-affected requires --affected-root")
        affected_replacements = load_affected_replacements(
            args.affected_root.resolve()
        )
        overlap = set(replacements) & set(affected_replacements)
        if len(overlap) != 82:
            raise SystemExit(
                f"expected 82 prior rerun cells to be superseded, got "
                f"{len(overlap)}"
            )
        replacements.update(affected_replacements)
    if args.include_environment:
        if args.environment_root is None:
            raise SystemExit(
                "--include-environment requires --environment-root"
            )
        environment_replacements = load_environment_replacements(
            args.environment_root.resolve()
        )
        overlap = set(replacements) & set(environment_replacements)
        if len(overlap) != 91:
            raise SystemExit(
                f"expected 91 prior rerun cells to be superseded, got "
                f"{len(overlap)}"
            )
        replacements.update(environment_replacements)

    replacement_counts = Counter(
        replacement["outcome_source"] for replacement in replacements.values()
    )
    trajectories = merge_artifact_rows(replacements)
    outcomes = outcome_rows(original_rows, replacements)
    write_final_outcomes(outcomes)
    write_final_result_export(trajectories)
    if recovery_replacements:
        write_recovery_csv(recovery_replacements)
    update_numeric_summaries(outcomes, trajectories, replacement_counts)
    update_indexes(trajectories)
    print(
        f"rebuilt {len(outcomes)} outcomes and artifacts with "
        f"{dict(replacement_counts)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
