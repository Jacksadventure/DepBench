#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

from __future__ import annotations

import argparse
import gzip
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read_row(path: Path, task: str) -> dict:
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        for line in handle:
            row = json.loads(line)
            if row.get("task") == task:
                return row
    raise SystemExit(f"task {task!r} not found in {path}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--configuration", required=True, help="file stem such as gpt55__codex")
    parser.add_argument("--task", required=True, help="task folder name")
    parser.add_argument(
        "--artifact-root",
        type=Path,
        default=ROOT,
        help="Directory containing trajectories/ and verify_logs/ (e.g. paper_review).",
    )
    parser.add_argument("--show-trajectory", action="store_true")
    parser.add_argument("--show-verifier", action="store_true")
    args = parser.parse_args()

    stem = args.configuration
    trajectory_path = args.artifact_root / "trajectories" / f"{stem}.jsonl.gz"
    verifier_path = args.artifact_root / "verify_logs" / f"{stem}.jsonl.gz"
    if not trajectory_path.exists():
        raise SystemExit(f"configuration not found: {stem}")

    trajectory_row = read_row(trajectory_path, args.task)
    metadata = {k: v for k, v in trajectory_row.items() if k != "trajectory"}
    print(json.dumps(metadata, indent=2, sort_keys=True))

    if args.show_trajectory:
        print(json.dumps(trajectory_row.get("trajectory"), indent=2, sort_keys=True))

    if args.show_verifier:
        verifier_row = read_row(verifier_path, args.task)
        print(json.dumps(verifier_row, indent=2, sort_keys=True))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
