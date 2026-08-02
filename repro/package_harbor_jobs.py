#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""Package a completed Harbor rerun without agent caches or session state."""

from __future__ import annotations

import argparse
import base64
import csv
import hashlib
import io
import json
import os
import re
import tarfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_CONFIGURATIONS = {
    "claude_code__claude48",
    "claude_code__gemini35flash",
    "claude_code__gpt55",
    "codex__gpt55",
    "copilot_cli__claude48",
    "copilot_cli__gemini35flash",
    "copilot_cli__gpt55",
    "opencode__claude48",
    "opencode__gemini35flash",
    "opencode__gpt55",
}
MAX_ARCHIVE_BYTES = 95 * 1024 * 1024
EXCLUDED_DIRECTORIES = {
    "sessions",
    ".tmp",
    ".cache",
    ".venv",
    "auth",
    "cache",
    "credentials",
    "node_modules",
    "skills",
    "setup",
    "shell_snapshots",
    "memories",
    "venv",
    "__pycache__",
}
EXCLUDED_SUFFIXES = (
    ".db",
    ".pyc",
    ".sqlite",
    ".sqlite3",
    ".sqlite-shm",
    ".sqlite-wal",
)
PUBLIC_AGENT_FILES = {
    "blocked_repo.txt",
    "claude-code.txt",
    "codex.txt",
    "copilot-cli.jsonl",
    "copilot-cli.txt",
    "git_history_pruned.txt",
    "opencode.txt",
    "trajectory.json",
}
TRIAL_ENTRIES = (
    "config.json",
    "result.json",
    "trial.log",
    "exception.txt",
    "artifacts",
    "agent",
    "verifier",
)
METADATA_ENTRIES = (
    "RUN_INFO.md",
    "run_all.sh",
    "run_all_path_fix.sh",
    "run_infra_retries.sh",
    "run_retries.sh",
    "run_supplemental_retries.sh",
    "run_supplemental2_retries.sh",
    "configs",
    "configs_retries",
    "configs_retries_supplemental",
    "configs_retries_supplemental2",
    "configs_path_fix",
    "configs_path_fix_retries",
    "manifests",
    "analysis",
    "launcher_logs",
    "launcher_logs_retries",
    "launcher_logs_retries_supplemental",
    "launcher_logs_retries_supplemental2",
    "launcher_logs_path_fix",
    "launcher_logs_path_fix_retries",
    "custom_agents",
)
REQUIRED_RAW_TRIAL_FILES = (
    "config.json",
    "result.json",
    "trial.log",
)
REQUIRED_SELECTED_TRIAL_FILES = (
    "verifier/reward.txt",
)
HOST_REDACTIONS = tuple(
    (
        base64.b64decode(encoded),
        replacement,
        label,
    )
    for encoded, replacement, label in (
        ("L0RhdGEyL3YtemlqaWFubHVv", b"$WORKSPACE", "workspace_path"),
        ("L2hvbWUvdi16aWppYW5sdW8=", b"$HOME", "home_path"),
        ("di16aWppYW5sdW8=", b"benchmark-user", "user_name"),
        ("Q09ERVhfTUFFU1RSTw==", b"AGENT_ENDPOINT", "internal_service"),
        ("bXNyNGFnZW50", b"agent-service", "internal_service"),
    )
)
SECRET_REDACTIONS = (
    (
        re.compile(
            rb"(?:github_pat_[A-Za-z0-9_]{20,}|"
            rb"gh[pousr]_[A-Za-z0-9]{30,})"
        ),
        b"$REDACTED_GITHUB_TOKEN",
        "github_token",
    ),
    (
        re.compile(rb"\b(?:sk-proj|sk|rk)-[A-Za-z0-9_-]{20,}\b"),
        b"$REDACTED_OPENAI_KEY",
        "openai_key",
    ),
    (
        re.compile(rb"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b"),
        b"$REDACTED_AWS_ACCESS_KEY",
        "aws_access_key",
    ),
)


def ensure_inside(root: Path, path: Path) -> Path:
    resolved = path.resolve()
    try:
        resolved.relative_to(root)
    except ValueError as error:
        raise SystemExit(f"path escapes the run root: {path}") from error
    return resolved


def reject_symlink(path: Path) -> None:
    if path.is_symlink():
        raise SystemExit(f"refusing to package symbolic link: {path}")


def walk_error(error: OSError) -> None:
    raise error


def included_files(path: Path, *, run_root: Path) -> list[Path]:
    reject_symlink(path)
    ensure_inside(run_root, path)
    if path.is_file():
        return [path]
    if not path.is_dir():
        return []
    if path.name == "agent":
        output = []
        for name in sorted(PUBLIC_AGENT_FILES):
            child = path / name
            reject_symlink(child)
            if child.is_file():
                ensure_inside(run_root, child)
                output.append(child)
        return output
    output = []
    for current_text, directories, files in os.walk(
        path, followlinks=False, onerror=walk_error
    ):
        current = Path(current_text)
        retained = []
        for name in sorted(directories):
            child = current / name
            reject_symlink(child)
            if name not in EXCLUDED_DIRECTORIES:
                ensure_inside(run_root, child)
                retained.append(name)
        directories[:] = retained
        for name in sorted(files):
            child = current / name
            reject_symlink(child)
            ensure_inside(run_root, child)
            if child.is_file() and not name.endswith(EXCLUDED_SUFFIXES):
                output.append(child)
    return output


def add_path(
    archive: tarfile.TarFile,
    *,
    run_root: Path,
    path: Path,
    redactions: Counter[str],
) -> None:
    for source in included_files(path, run_root=run_root):
        payload = source.read_bytes()
        replacements = (
            (str(run_root).encode(), b"$RUN_ROOT", "run_root"),
            *HOST_REDACTIONS,
        )
        for old, new, label in replacements:
            count = payload.count(old)
            if count:
                payload = payload.replace(old, new)
                redactions[label] += count
        for pattern, replacement, label in SECRET_REDACTIONS:
            payload, count = pattern.subn(replacement, payload)
            if count:
                redactions[label] += count
        relative = source.relative_to(run_root)
        if relative.is_absolute() or ".." in relative.parts:
            raise SystemExit(f"unsafe archive member path: {relative}")
        info = archive.gettarinfo(str(source), arcname=relative.as_posix())
        if not info.isfile():
            raise SystemExit(f"non-regular archive member: {source}")
        info.uid = 0
        info.gid = 0
        info.uname = "root"
        info.gname = "root"
        info.size = len(payload)
        archive.addfile(info, io.BytesIO(payload))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    run_root = args.run_root.resolve()
    output_dir = args.output_dir.resolve()
    ensure_inside(ROOT, output_dir)
    if output_dir.exists() and any(output_dir.iterdir()):
        raise SystemExit(
            f"output directory must be absent or empty: {output_dir}"
        )
    if not run_root.is_dir():
        raise SystemExit(f"run root does not exist: {run_root}")
    rows = list(
        csv.DictReader(
            (run_root / "analysis/final_trials.csv").open(encoding="utf-8")
        )
    )
    all_trials_path = run_root / "analysis/all_trials.csv"
    if not all_trials_path.is_file():
        raise SystemExit("analysis/all_trials.csv is required")
    all_rows = list(
        csv.DictReader(all_trials_path.open(encoding="utf-8"))
    )
    configurations = {row["config"] for row in rows}
    tasks = {row["task"] for row in rows}
    cells = {(row["config"], row["task"]) for row in rows}
    task_manifests = sorted(
        (run_root / "manifests").glob("affected_tasks_*.txt")
    )
    if len(task_manifests) != 1:
        raise SystemExit(
            "expected exactly one manifests/affected_tasks_*.txt file"
        )
    expected_tasks = {
        line.strip()
        for line in task_manifests[0].read_text(
            encoding="utf-8"
        ).splitlines()
        if line.strip()
    }
    expected_cells = len(expected_tasks) * len(EXPECTED_CONFIGURATIONS)
    if (
        len(rows) != expected_cells
        or configurations != EXPECTED_CONFIGURATIONS
        or tasks != expected_tasks
        or not expected_tasks
        or len(cells) != expected_cells
    ):
        raise SystemExit(
            "expected a complete task-manifest x 10-configuration final "
            "trial set"
        )
    if (
        {row["config"] for row in all_rows} != EXPECTED_CONFIGURATIONS
        or {row["task"] for row in all_rows} - expected_tasks
        or len({row["path"] for row in all_rows}) != len(all_rows)
        or {row["path"] for row in rows}
        - {row["path"] for row in all_rows}
    ):
        raise SystemExit("all_trials.csv does not contain valid raw trials")
    expected_raw_paths = set()
    for source in (
        "harbor_jobs",
        "harbor_jobs_path_fix",
        "harbor_jobs_path_fix_retries",
        "harbor_jobs_retries",
    ):
        source_root = run_root / source
        if source_root.is_dir():
            observed_configurations = {
                path.name for path in source_root.iterdir() if path.is_dir()
            }
            unexpected_configurations = (
                observed_configurations - EXPECTED_CONFIGURATIONS
            )
            if unexpected_configurations:
                raise SystemExit(
                    f"{source} contains unexpected configuration "
                    f"directories: {sorted(unexpected_configurations)}"
                )
        for configuration in EXPECTED_CONFIGURATIONS:
            directory = source_root / configuration
            if not directory.is_dir():
                continue
            expected_raw_paths.update(
                str(path.relative_to(run_root))
                for path in directory.glob("*/*/result.json")
            )
    observed_raw_paths = {row["path"] for row in all_rows}
    if observed_raw_paths != expected_raw_paths:
        raise SystemExit(
            "all_trials.csv does not exactly inventory the raw job trees: "
            f"missing={len(expected_raw_paths - observed_raw_paths)} "
            f"extra={len(observed_raw_paths - expected_raw_paths)}"
        )

    trial_directories = set()
    selected_paths = {row["path"] for row in rows}
    for row in all_rows:
        relative = Path(row["path"])
        if relative.is_absolute() or ".." in relative.parts:
            raise SystemExit(f"unsafe result path in final_trials.csv: {relative}")
        expected_prefixes = {
            ("harbor_jobs", row["config"]),
            ("harbor_jobs_path_fix", row["config"]),
            ("harbor_jobs_path_fix_retries", row["config"]),
            ("harbor_jobs_retries", row["config"]),
        }
        if (
            len(relative.parts) != 5
            or relative.parts[:2] not in expected_prefixes
            or relative.name != "result.json"
        ):
            raise SystemExit(f"unexpected result path: {relative}")
        result_path = ensure_inside(run_root, run_root / relative)
        if not result_path.is_file():
            raise SystemExit(f"missing result file: {result_path}")
        trial_dir = result_path.parent
        if trial_dir in trial_directories:
            raise SystemExit(f"duplicate trial directory: {trial_dir}")
        trial_directories.add(trial_dir)
        try:
            result = json.loads(result_path.read_text(encoding="utf-8"))
            observed_task = str(
                result.get("task_name") or ""
            ).split("/")[-1]
        except json.JSONDecodeError:
            if row["path"] in selected_paths:
                raise SystemExit(
                    f"selected result is malformed: {result_path}"
                )
            observed_task = row["task"]
        if observed_task != row["task"]:
            raise SystemExit(
                f"{result_path}: task {observed_task!r} != {row['task']!r}"
            )
        for required in REQUIRED_RAW_TRIAL_FILES:
            required_path = trial_dir / required
            reject_symlink(required_path)
            if not required_path.is_file():
                raise SystemExit(f"missing required trial file: {required_path}")
        if row["path"] not in selected_paths:
            continue
        agent_timeout_without_reward = (
            row.get("exception_type") == "AgentTimeoutError"
            and row.get("reward_available", "").lower() == "false"
        )
        if not agent_timeout_without_reward:
            for required in REQUIRED_SELECTED_TRIAL_FILES:
                required_path = trial_dir / required
                reject_symlink(required_path)
                if not required_path.is_file():
                    raise SystemExit(
                        f"selected trial is missing required file: "
                        f"{required_path}"
                    )
            verifier_evidence = (
                trial_dir / "verifier/test-stdout.txt",
                trial_dir / "verifier/ctrf.json",
            )
            if not any(path.is_file() for path in verifier_evidence):
                raise SystemExit(
                    f"missing verifier evidence under {trial_dir}"
                )
        agent_dir = trial_dir / "agent"
        if not any((agent_dir / name).is_file() for name in PUBLIC_AGENT_FILES):
            raise SystemExit(f"missing public agent log under {trial_dir}")

    archives_dir = output_dir / "archives"
    archives_dir.mkdir(parents=True, exist_ok=True)
    archive_rows = []
    redactions: Counter[str] = Counter()
    for configuration in sorted(configurations):
        subset = [
            row for row in all_rows if row["config"] == configuration
        ]
        selected_subset = [
            row for row in rows if row["config"] == configuration
        ]
        archive_path = archives_dir / f"{configuration}.tar.gz"
        with tarfile.open(
            archive_path, "w:gz", compresslevel=6
        ) as archive:
            add_path(
                archive,
                run_root=run_root,
                path=run_root / "configs" / f"{configuration}.json",
                redactions=redactions,
            )
            add_path(
                archive,
                run_root=run_root,
                path=(
                    run_root
                    / "configs_retries_supplemental2"
                    / f"{configuration}.json"
                ),
                redactions=redactions,
            )
            add_path(
                archive,
                run_root=run_root,
                path=(
                    run_root
                    / "configs_retries"
                    / f"{configuration}.json"
                ),
                redactions=redactions,
            )
            add_path(
                archive,
                run_root=run_root,
                path=(
                    run_root
                    / "configs_retries_supplemental"
                    / f"{configuration}.json"
                ),
                redactions=redactions,
            )
            for logs_directory in (
                "launcher_logs",
                "launcher_logs_retries",
                "launcher_logs_retries_supplemental",
                "launcher_logs_retries_supplemental2",
                "launcher_logs_path_fix",
                "launcher_logs_path_fix_retries",
            ):
                for suffix in ("log", "status"):
                    add_path(
                        archive,
                        run_root=run_root,
                        path=(
                            run_root
                            / logs_directory
                            / f"{configuration}.{suffix}"
                        ),
                        redactions=redactions,
                    )
            for row in sorted(subset, key=lambda item: item["task"]):
                trial_dir = (run_root / row["path"]).parent
                for entry in TRIAL_ENTRIES:
                    add_path(
                        archive,
                        run_root=run_root,
                        path=trial_dir / entry,
                        redactions=redactions,
                    )
        if archive_path.stat().st_size >= MAX_ARCHIVE_BYTES:
            raise SystemExit(
                f"{archive_path} exceeds the 95 MiB publication limit"
            )
        archive_rows.append(
            {
                "configuration": configuration,
                "trials": len(subset),
                "selected_trials": len(selected_subset),
                "file": str(archive_path.relative_to(output_dir)),
                "bytes": archive_path.stat().st_size,
                "sha256": sha256(archive_path),
            }
        )

    metadata_path = archives_dir / "run_metadata.tar.gz"
    with tarfile.open(metadata_path, "w:gz", compresslevel=6) as archive:
        for entry in METADATA_ENTRIES:
            if not (run_root / entry).exists():
                continue
            add_path(
                archive,
                run_root=run_root,
                path=run_root / entry,
                redactions=redactions,
            )
    if metadata_path.stat().st_size >= MAX_ARCHIVE_BYTES:
        raise SystemExit(
            f"{metadata_path} exceeds the 95 MiB publication limit"
        )
    archive_rows.append(
        {
            "configuration": "run_metadata",
            "trials": len(all_rows),
            "selected_trials": len(rows),
            "file": str(metadata_path.relative_to(output_dir)),
            "bytes": metadata_path.stat().st_size,
            "sha256": sha256(metadata_path),
        }
    )

    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "run": run_root.name,
        "tasks": len(tasks),
        "configurations": len(configurations),
        "trials": len(rows),
        "raw_trials": len(all_rows),
        "replacement_trials": len(all_rows) - len(rows),
        "format": "gzip-compressed POSIX tar archives",
        "excluded": [
            "agent session directories",
            "agent plugin/temp/skill caches",
            "agent shell snapshots, memories, and setup state",
            "agent authentication, installation, and local state files",
            "SQLite state files",
            "Python bytecode caches",
        ],
        "redactions": dict(sorted(redactions.items())),
        "source_hash_manifests_are_pre_redaction": True,
        "archives": archive_rows,
    }
    (output_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (output_dir / "README.md").write_text(
        "# Targeted DepBench Harbor jobs\n\n"
        f"These archives contain the {len(tasks)}-task by "
        "10-configuration rerun used "
        "to update the final results. Each configuration archive preserves "
        "all original and infrastructure-retry "
        "Harbor trials. Completed trials include result metadata, patches, "
        "raw agent logs, recovered trajectories, and verifier outputs; "
        "pre-verifier setup failures retain their result and trial logs. "
        "`run_metadata.tar.gz` contains "
        "the frozen configurations, task/image manifests, launcher logs, "
        "analysis summaries, and custom adapters.\n\n"
        "Agent authentication/install state, session stores, plugin caches, "
        "SQLite state, and bytecode caches are excluded because they are not "
        "required to reproduce or audit the selected trials. Host paths, "
        "usernames, internal service labels, and credential-like token "
        "strings are replaced with stable placeholders; counts and "
        "archive SHA-256 hashes are recorded in `manifest.json`. Hash files "
        "inside `run_metadata.tar.gz` describe the pre-redaction run root and "
        "therefore may differ for path-bearing archived members.\n",
        encoding="utf-8",
    )
    print(
        f"packaged {len(rows)} trials into {len(archive_rows)} archives at "
        f"{output_dir}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
