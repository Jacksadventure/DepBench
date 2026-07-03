#!/usr/bin/env python3
from __future__ import annotations

import csv
import gzip
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def count_gzip_jsonl(path: Path) -> int:
    count = 0
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        for line in handle:
            json.loads(line)
            count += 1
    return count


def main() -> int:
    task_summary = json.loads((ROOT / "dataset/task_summary.json").read_text())
    task_dirs = [p for p in (ROOT / "dataset/tasks").iterdir() if p.is_dir()]
    if len(task_summary) != 219 or len(task_dirs) != 219:
        raise SystemExit(f"expected 219 tasks, got summary={len(task_summary)} dirs={len(task_dirs)}")

    summary_rows = list(csv.DictReader((ROOT / "results/summary.csv").open()))
    if len(summary_rows) != 10:
        raise SystemExit(f"expected 10 configurations, got {len(summary_rows)}")

    for directory in ("trajectories", "verify_logs"):
        files = sorted((ROOT / directory).glob("*.jsonl.gz"))
        if len(files) != 10:
            raise SystemExit(f"expected 10 {directory} files, got {len(files)}")
        for path in files:
            rows = count_gzip_jsonl(path)
            if rows != 219:
                raise SystemExit(f"{path}: expected 219 rows, got {rows}")

    per_trial_rows = count_gzip_jsonl(ROOT / "results/per_trial_results.jsonl.gz")
    if per_trial_rows != 2190:
        raise SystemExit(f"expected 2190 per-trial rows, got {per_trial_rows}")

    required = [
        "README.md",
        "MANIFEST.json",
        "pyproject.toml",
        "analysis/ecosystem_results.csv",
        "analysis/coverage.csv",
        "repro/TASK_SCHEMA.md",
        "repro/run_oracle_solution.sh",
        "repro/run_patch_verifier.sh",
        "repro/HARBOR.md",
        "repro/make_harbor_config.py",
        "custom_agents/codex.py",
        "custom_agents/copilot_cli.py",
        "custom_agents/opencode.py",
        "custom_agents/claude_code.py",
    ]
    missing = [path for path in required if not (ROOT / path).exists()]
    if missing:
        raise SystemExit(f"missing required files: {missing}")

    example_configs = sorted((ROOT / "repro/examples").glob("*.json"))
    if len(example_configs) != 10:
        raise SystemExit(f"expected 10 Harbor example configs, got {len(example_configs)}")
    for path in example_configs:
        config = json.loads(path.read_text())
        if config["datasets"][0]["path"] != "dataset/tasks":
            raise SystemExit(f"{path}: expected dataset/tasks relative path")

    print("DepBench release validation passed: 219 tasks, 10 configurations, 2190 reported trials.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
