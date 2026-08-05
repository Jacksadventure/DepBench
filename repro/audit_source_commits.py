#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""Verify that every recorded source commit is fetchable via Git."""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_METADATA = ROOT / "analysis/task_source_builds.csv"
DEFAULT_OUTPUT = ROOT / "analysis/source_commit_audit_201.csv"
FIELDS = [
    "task",
    "repository_url",
    "base_commit",
    "fetch_status",
    "resolved_commit",
    "duration_seconds",
    "audited_at",
    "error",
]


def audit_one(source: dict[str, str]) -> dict[str, str]:
    started = time.monotonic()
    row = {field: "" for field in FIELDS}
    row.update(
        {
            "task": source["task"],
            "repository_url": source["repository_url"],
            "base_commit": source["base_commit"],
            "audited_at": datetime.now(timezone.utc).isoformat(),
        }
    )
    try:
        with tempfile.TemporaryDirectory(prefix="depbench-source-commit-") as temporary:
            subprocess.run(
                ["git", "init", "--bare", temporary],
                text=True,
                check=True,
                capture_output=True,
                timeout=60,
            )
            fetch = subprocess.run(
                [
                    "git",
                    "-C",
                    temporary,
                    "-c",
                    "protocol.version=2",
                    "fetch",
                    "--depth=1",
                    "--filter=blob:none",
                    source["repository_url"],
                    source["base_commit"],
                ],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                timeout=600,
            )
            if fetch.returncode != 0:
                raise RuntimeError(f"git fetch failed: {fetch.stdout[-2000:]}")
            resolved = subprocess.run(
                [
                    "git",
                    "-C",
                    temporary,
                    "rev-parse",
                    "FETCH_HEAD^{commit}",
                ],
                text=True,
                check=True,
                capture_output=True,
                timeout=60,
            ).stdout.strip()
            if resolved != source["base_commit"]:
                raise RuntimeError(
                    f"resolved commit differs: {resolved} != {source['base_commit']}"
                )
            row["fetch_status"] = "pass"
            row["resolved_commit"] = resolved
    except subprocess.TimeoutExpired as error:
        row["error"] = f"timeout after {error.timeout} seconds"
    except Exception as error:  # noqa: BLE001 - preserve one result per task
        row["error"] = str(error).replace("\n", " ")[:4000]
    row["duration_seconds"] = f"{time.monotonic() - started:.1f}"
    return row


def write_rows(path: Path, rows: dict[str, dict[str, str]]) -> None:
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
    parser.add_argument("--jobs", type=int, default=8)
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()

    sources = list(csv.DictReader(args.metadata.open(encoding="utf-8")))
    source_by_task = {source["task"]: source for source in sources}
    if len(sources) != 201 or len(source_by_task) != 201:
        raise SystemExit("source metadata must contain 201 unique tasks")

    rows: dict[str, dict[str, str]] = {}
    if args.resume and args.output.exists():
        rows = {
            row["task"]: row
            for row in csv.DictReader(args.output.open(encoding="utf-8"))
            if row["fetch_status"] == "pass"
            and not row["error"]
            and row["task"] in source_by_task
            and row["repository_url"]
            == source_by_task[row["task"]]["repository_url"]
            and row["base_commit"]
            == source_by_task[row["task"]]["base_commit"]
        }
    pending = [source for source in sources if source["task"] not in rows]
    print(f"checking {len(pending)} source commits with {args.jobs} workers")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(max_workers=args.jobs) as executor:
        futures = {
            executor.submit(audit_one, source): source["task"] for source in pending
        }
        for future in as_completed(futures):
            task = futures[future]
            row = future.result()
            rows[task] = row
            write_rows(args.output.resolve(), rows)
            status = "PASS" if not row["error"] else "FAIL"
            print(f"{status} {task} ({row['duration_seconds']}s)", flush=True)

    failures = [row for row in rows.values() if row["error"]]
    print(f"source-commit audit: {len(rows) - len(failures)}/{len(rows)} passed")
    if failures:
        for row in sorted(failures, key=lambda item: item["task"]):
            print(f"- {row['task']}: {row['error'][:500]}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
