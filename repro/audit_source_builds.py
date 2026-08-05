#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""Build and inspect every source-based DepBench task image."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import subprocess
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_METADATA = ROOT / "analysis/task_source_builds.csv"
DEFAULT_OUTPUT = ROOT / "analysis/source_build_audit_201.csv"
DEFAULT_LOGS = ROOT / ".source-build-audit-logs"
FIELDS = [
    "task",
    "repository_url",
    "base_commit",
    "base_image",
    "base_image_digest",
    "dockerfile_sha256",
    "static_status",
    "build_status",
    "runtime_status",
    "git_head_status",
    "worktree_status",
    "duration_seconds",
    "audited_at",
    "error",
]


def run(
    command: list[str],
    *,
    timeout: float | None = None,
    log_path: Path | None = None,
) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        command,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=timeout,
    )
    if log_path is not None:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log_path.write_text(result.stdout, encoding="utf-8", errors="replace")
    return result


def toolchain_check(base_image: str, dockerfile: str) -> str:
    checks = []
    if base_image.startswith("golang:"):
        checks.append("command -v go; go version; command -v gofmt")
    if base_image.startswith("rust:") or "rustup.rs" in dockerfile:
        checks.append(
            "command -v cargo; cargo --version; "
            "command -v rustc; rustc --version"
        )
    if base_image.startswith("maven:"):
        checks.append(
            'test "$JAVA_HOME" = /opt/java/openjdk; '
            "command -v java; java -version; command -v mvn; mvn -version"
        )
    if base_image.startswith("node:"):
        checks.append("command -v node; node --version; command -v npm; npm --version")
        if "yarn " in dockerfile:
            checks.append("command -v yarn; yarn --version")
        if "pnpm " in dockerfile:
            checks.append("command -v pnpm; pnpm --version")
    if base_image.startswith("python:"):
        checks.append("command -v python; python --version; command -v pip; pip --version")
    if base_image.startswith("elixir:"):
        checks.append("command -v elixir; elixir --version; command -v mix; mix --version")
    if not checks:
        raise ValueError(f"unsupported base image: {base_image}")
    return "; ".join(checks)


def base_digest(image: str, cache: dict[str, str], lock: threading.Lock) -> str:
    with lock:
        if image in cache:
            return cache[image]
    result = run(["crane", "digest", image], timeout=300)
    if result.returncode != 0:
        raise RuntimeError(f"base image unavailable: {result.stdout[-1000:]}")
    digest = result.stdout.strip()
    with lock:
        cache[image] = digest
    return digest


def audit_one(
    source: dict[str, str],
    *,
    logs_dir: Path,
    image_prefix: str,
    digest_cache: dict[str, str],
    digest_lock: threading.Lock,
) -> dict[str, str]:
    started = time.monotonic()
    task = source["task"]
    task_dir = ROOT / "dataset/tasks" / task
    dockerfile_path = task_dir / "environment/Dockerfile"
    row = {field: "" for field in FIELDS}
    row.update({field: source[field] for field in source if field in row})
    row["audited_at"] = datetime.now(timezone.utc).isoformat()
    try:
        dockerfile = dockerfile_path.read_text(encoding="utf-8")
        digest = hashlib.sha256(dockerfile.encode()).hexdigest()
        if digest != source["dockerfile_sha256"]:
            raise RuntimeError("Dockerfile checksum differs from source metadata")
        if "git clone" not in dockerfile or source["base_commit"] not in dockerfile:
            raise RuntimeError("Dockerfile does not clone and checkout the recorded source")
        if "manifest.patch" in dockerfile or "\nCOPY " in dockerfile:
            raise RuntimeError("Dockerfile exposes packaged benchmark patches")
        task_toml_text = (task_dir / "task.toml").read_text(encoding="utf-8")
        if "docker_image" in task_toml_text:
            raise RuntimeError("task.toml still references a prebuilt image")
        if (task_dir / "environment/docker-compose.yaml").exists():
            raise RuntimeError("placeholder docker-compose.yaml remains")
        row["static_status"] = "pass"

        row["base_image_digest"] = base_digest(
            source["base_image_reference"], digest_cache, digest_lock
        )
        if row["base_image_digest"] != source["base_image_digest"]:
            raise RuntimeError("pinned base-image manifest is unavailable")
        timeout_match = re.search(
            r"^build_timeout_sec\s*=\s*([0-9.]+)\s*$",
            task_toml_text,
            re.MULTILINE,
        )
        timeout = float(timeout_match.group(1) if timeout_match else 1800)
        image = f"{image_prefix}:{task}"
        build = run(
            [
                "docker",
                "build",
                "--pull",
                "--progress=plain",
                "--tag",
                image,
                str(task_dir / "environment"),
            ],
            timeout=timeout,
            log_path=logs_dir / f"{task}.build.log",
        )
        if build.returncode != 0:
            raise RuntimeError(f"docker build failed: {build.stdout[-2000:]}")
        row["build_status"] = "pass"

        check = (
            "set -euo pipefail; "
            f'test "$(git -C /app rev-parse HEAD)" = "{source["base_commit"]}"; '
            'test -z "$(git -C /app status --porcelain)"; '
            + toolchain_check(source["base_image"], dockerfile)
        )
        runtime = run(
            [
                "docker",
                "run",
                "--rm",
                "--entrypoint",
                "/bin/bash",
                image,
                "-lc",
                check,
            ],
            timeout=300,
            log_path=logs_dir / f"{task}.runtime.log",
        )
        if runtime.returncode != 0:
            raise RuntimeError(f"runtime inspection failed: {runtime.stdout[-2000:]}")
        row["runtime_status"] = "pass"
        row["git_head_status"] = "pass"
        row["worktree_status"] = "pass"
    except subprocess.TimeoutExpired as error:
        row["error"] = f"timeout after {error.timeout} seconds"
    except Exception as error:  # noqa: BLE001 - each task must produce an audit row
        row["error"] = str(error).replace("\n", " ")[:4000]
    row["duration_seconds"] = f"{time.monotonic() - started:.1f}"
    return row


def write_rows(path: Path, rows: dict[str, dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".csv.tmp")
    with temporary.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=FIELDS,
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows[task] for task in sorted(rows))
    temporary.replace(path)
    path.with_suffix(".json").write_text(
        json.dumps([rows[task] for task in sorted(rows)], indent=2) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", type=Path, default=DEFAULT_METADATA)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--logs-dir", type=Path, default=DEFAULT_LOGS)
    parser.add_argument("--jobs", type=int, default=2)
    parser.add_argument("--image-prefix", default="depbench-source-audit")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--task", action="append")
    args = parser.parse_args()

    sources = list(csv.DictReader(args.metadata.open(encoding="utf-8")))
    if len(sources) != 201 or len({row["task"] for row in sources}) != 201:
        raise SystemExit("source metadata must contain 201 unique tasks")

    source_by_task = {source["task"]: source for source in sources}
    rows: dict[str, dict[str, str]] = {}
    if args.resume and args.output.exists():
        rows = {
            row["task"]: row
            for row in csv.DictReader(args.output.open(encoding="utf-8"))
            if row["build_status"] == "pass"
            and row["runtime_status"] == "pass"
            and row["git_head_status"] == "pass"
            and row["worktree_status"] == "pass"
            and row["task"] in source_by_task
            and row["dockerfile_sha256"]
            == source_by_task[row["task"]]["dockerfile_sha256"]
        }
    selected = set(args.task or ())
    unknown = selected - {source["task"] for source in sources}
    if unknown:
        raise SystemExit(f"unknown tasks: {sorted(unknown)}")
    pending = [
        source
        for source in sources
        if source["task"] not in rows
        and (not selected or source["task"] in selected)
    ]
    print(f"auditing {len(pending)} tasks with {args.jobs} workers")

    digest_cache: dict[str, str] = {}
    digest_lock = threading.Lock()
    with ThreadPoolExecutor(max_workers=args.jobs) as executor:
        futures = {
            executor.submit(
                audit_one,
                source,
                logs_dir=args.logs_dir.resolve(),
                image_prefix=args.image_prefix,
                digest_cache=digest_cache,
                digest_lock=digest_lock,
            ): source["task"]
            for source in pending
        }
        for future in as_completed(futures):
            task = futures[future]
            row = future.result()
            rows[task] = row
            write_rows(args.output.resolve(), rows)
            status = "PASS" if not row["error"] else "FAIL"
            print(f"{status} {task} ({row['duration_seconds']}s)", flush=True)

    failures = [row for row in rows.values() if row["error"]]
    print(f"source-build audit: {len(rows) - len(failures)}/{len(rows)} passed")
    if failures:
        print("failed tasks:")
        for row in sorted(failures, key=lambda item: item["task"]):
            print(f"- {row['task']}: {row['error'][:500]}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
