#!/usr/bin/env python3
from __future__ import annotations

import csv
import gzip
import json
from collections import Counter
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
    active_tasks = {row["folder"] for row in task_summary}
    if len(task_summary) != 203 or len(task_dirs) != 203:
        raise SystemExit(f"expected 203 tasks, got summary={len(task_summary)} dirs={len(task_dirs)}")
    if active_tasks != {path.name for path in task_dirs}:
        raise SystemExit("task_summary folders do not match dataset/tasks")

    invalid_tasks = [
        path.parent.name
        for path in (ROOT / "dataset/tasks").glob("*/task.toml")
        if 'test_contract_status = "invalid"' in path.read_text()
    ]
    if invalid_tasks:
        raise SystemExit(f"expected no active invalid test contracts, got {invalid_tasks}")

    decision_rows = list(
        csv.DictReader(
            (ROOT / "analysis/test_contract_repair_decisions_2026-07-14.csv").open()
        )
    )
    decision_counts = {
        decision: sum(row["decision"] == decision for row in decision_rows)
        for decision in ("repair", "repackage", "mark_invalid")
    }
    if len(decision_rows) != 37 or decision_counts != {
        "repair": 8,
        "repackage": 13,
        "mark_invalid": 16,
    }:
        raise SystemExit(
            f"unexpected test contract decisions: rows={len(decision_rows)} "
            f"counts={decision_counts}"
        )
    removed_tasks = {
        row["task"] for row in decision_rows if row["decision"] == "mark_invalid"
    }
    if len(removed_tasks) != 16 or active_tasks & removed_tasks:
        raise SystemExit("invalid test-contract removal is incomplete")

    summary_rows = list(csv.DictReader((ROOT / "results/summary.csv").open()))
    if len(summary_rows) != 10:
        raise SystemExit(f"expected 10 configurations, got {len(summary_rows)}")
    if any(int(row["tasks"]) != 203 for row in summary_rows):
        raise SystemExit("results summary does not use the 203-task denominator")

    final_outcomes = list(
        csv.DictReader((ROOT / "results/final_per_task_outcomes.csv").open())
    )
    if len(final_outcomes) != 2030:
        raise SystemExit(f"expected 2030 final outcomes, got {len(final_outcomes)}")
    if {row["task"] for row in final_outcomes} != active_tasks:
        raise SystemExit("final outcome tasks do not match the release")
    if sum(row["outcome_source"] == "targeted_rerun" for row in final_outcomes) != 111:
        raise SystemExit("expected 111 targeted rerun outcomes")
    rerun_rows = list(
        csv.DictReader(
            (ROOT / "results/targeted_runtime_exception_reruns_203.csv").open()
        )
    )
    if len(rerun_rows) != 111 or len(
        {(row["configuration"], row["task"]) for row in rerun_rows}
    ) != 111:
        raise SystemExit("expected 111 unique targeted rerun cells")

    for summary in summary_rows:
        configuration = f"{summary['llm']}__{summary['harness']}"
        subset = [
            row for row in final_outcomes if row["configuration"] == configuration
        ]
        counts = Counter(
            "pass"
            if row["final_reward"] == "1.0"
            else "no_reward"
            if row["final_reward"] == ""
            else "fail"
            for row in subset
        )
        observed = (
            len(subset),
            counts["pass"],
            counts["fail"],
            counts["no_reward"],
        )
        expected = tuple(
            int(summary[field]) for field in ("tasks", "pass", "fail", "no_reward")
        )
        if observed != expected:
            raise SystemExit(
                f"{configuration}: final outcomes {observed} != summary {expected}"
            )

    task_ecosystems = {row["folder"]: row["ecosystem"] for row in task_summary}
    llm_names = {
        "claude-opus-4-8": "claude48",
        "gemini-3.5-flash": "gemini35flash",
        "gpt-5.5": "gpt55",
    }
    ecosystem_rows = list(
        csv.DictReader((ROOT / "analysis/ecosystem_results.csv").open())
    )
    for ecosystem in ecosystem_rows:
        configuration = (
            f"{llm_names[ecosystem['model']]}__{ecosystem['harness']}"
        )
        subset = [
            row
            for row in final_outcomes
            if row["configuration"] == configuration
            and task_ecosystems[row["task"]] == ecosystem["ecosystem"]
        ]
        counts = Counter(
            "pass"
            if row["final_reward"] == "1.0"
            else "no_reward"
            if row["final_reward"] == ""
            else "fail"
            for row in subset
        )
        observed = (
            len(subset),
            counts["pass"],
            counts["fail"],
            counts["no_reward"],
        )
        expected = tuple(
            int(ecosystem[field])
            for field in ("tasks", "pass", "fail", "no_reward")
        )
        if observed != expected:
            raise SystemExit(
                f"{configuration}/{ecosystem['ecosystem']}: "
                f"final outcomes {observed} != ecosystem summary {expected}"
            )

    repository_rows = list(
        csv.DictReader((ROOT / "analysis/repository_metadata.csv").open())
    )
    task_repository_rows = list(
        csv.DictReader((ROOT / "analysis/task_repository_metadata.csv").open())
    )
    if len(repository_rows) != 159 or len(task_repository_rows) != 203:
        raise SystemExit(
            "expected 159 repository rows and 203 task-repository rows, got "
            f"{len(repository_rows)} and {len(task_repository_rows)}"
        )
    if {row["task"] for row in task_repository_rows} != active_tasks:
        raise SystemExit("task repository metadata does not match the release")
    if sum(int(row["task_count"]) for row in repository_rows) != 203:
        raise SystemExit("repository metadata task counts do not sum to 203")
    if any(
        not row["repository_url"]
        or not row["license_spdx_id"]
        or not row["license_category"]
        or not row["primary_language"]
        for row in repository_rows
    ):
        raise SystemExit("repository metadata contains an incomplete required field")

    for directory in ("trajectories", "verify_logs"):
        files = sorted((ROOT / directory).glob("*.jsonl.gz"))
        if len(files) != 10:
            raise SystemExit(f"expected 10 {directory} files, got {len(files)}")
        for path in files:
            rows = count_gzip_jsonl(path)
            if rows != 203:
                raise SystemExit(f"{path}: expected 203 rows, got {rows}")

    per_trial_rows = count_gzip_jsonl(ROOT / "results/per_trial_results.jsonl.gz")
    if per_trial_rows != 2030:
        raise SystemExit(f"expected 2030 per-trial rows, got {per_trial_rows}")

    required = [
        "README.md",
        "MANIFEST.json",
        "pyproject.toml",
        "analysis/ecosystem_results.csv",
        "analysis/coverage.csv",
        "analysis/repository_metadata.csv",
        "analysis/repository_metadata.json",
        "analysis/task_repository_metadata.csv",
        "analysis/runtime_exception_rerun_summary_203.json",
        "analysis/test_contract_repair_decisions_2026-07-14.md",
        "analysis/test_contract_repair_decisions_2026-07-14.csv",
        "results/final_per_task_outcomes.csv",
        "results/targeted_runtime_exception_reruns_203.csv",
        "repro/collect_repository_metadata.py",
        "repro/sync_targeted_rerun_results.py",
        "repro/TASK_SCHEMA.md",
        "repro/run_oracle_solution.sh",
        "repro/run_patch_verifier.sh",
        "repro/scan_trajectories.py",
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
        if set(config["datasets"][0]["task_names"]) != active_tasks:
            raise SystemExit(f"{path}: task_names do not match the 203-task dataset")

    for path in [
        "analysis/trajectory_scan_detail.csv",
        "analysis/trajectory_scan_summary.csv",
        "analysis/trajectory_scan_summary.json",
    ]:
        if not (ROOT / path).exists():
            raise SystemExit(f"missing trajectory scan output: {path}")

    print("DepBench release validation passed: 203 tasks, 10 configurations, 2030 reported trials.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
