#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""Validate the separate historical paper-review cohort without running agents."""

from __future__ import annotations

import csv
import gzip
import json
import re
from collections import Counter
from pathlib import Path

from validate_release import CONFIGURATIONS, LICENSE_EXCLUDED_TASKS


ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / "paper_review"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def reward(value: str | float | None) -> float | None:
    if value is None or value == "":
        return None
    require(value in (0, 1, "0", "1", "0.0", "1.0"), "invalid verifier reward")
    return float(value)


def read_records(path: Path, *, trajectories: bool = False) -> dict:
    records = {}
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            row = json.loads(line)
            key = (f"{row['llm']}__{row['harness']}", row["task"])
            require(key not in records, f"{path}:{line_number}: duplicate {key}")
            if trajectories:
                trajectory = row.get("trajectory")
                require(
                    row.get("has_trajectory") is True
                    and isinstance(trajectory, dict)
                    and isinstance(trajectory.get("steps"), list)
                    and bool(trajectory["steps"]),
                    f"{path}:{line_number}: missing or empty trajectory",
                )
            records[key] = {
                "trial": row["trial"],
                "reward": reward(row.get("reward")),
                "stdout": bool(row.get("verifier_test_stdout")),
                "ctrf": bool(row.get("verifier_ctrf")),
            }
    return records


def main() -> int:
    manifest = json.loads((REVIEW / "MANIFEST.json").read_text())
    require(
        (manifest["tasks"], manifest["configurations"], manifest["total_trials"])
        == (203, 10, 2030),
        "review manifest must describe 203 tasks and 2030 selected trials",
    )
    tasks = json.loads((REVIEW / "dataset/task_summary.json").read_text())
    task_ids = {row["folder"] for row in tasks}
    require(len(tasks) == len(task_ids) == 203, "review task index is not unique")
    task_root = REVIEW / "dataset/tasks"
    require(
        {path.name for path in task_root.iterdir() if path.is_dir()} == task_ids,
        "review task directories do not match the task index",
    )
    main_ids = {
        row["task"] for row in csv_rows(ROOT / "analysis/task_repository_metadata.csv")
    }
    require(
        len(main_ids) == 201
        and task_ids == main_ids | LICENSE_EXCLUDED_TASKS,
        "review cohort is not main's 201 tasks plus the two historical tasks",
    )

    templates = set()
    for task in sorted(task_ids):
        task_dir = task_root / task
        for name in (
            "instruction.md",
            "task.toml",
            "environment/patches/manifest.patch",
            "solution/solve.sh",
            "tests/test.sh",
            "tests/test_state.py",
        ):
            require((task_dir / name).is_file(), f"{task}: missing {name}")
        text = (task_dir / "instruction.md").read_text()
        require(
            "Human Repair Commit Summary" not in text
            and "Original pull request:" not in text
            and not re.search(r"https?://", text),
            f"{task}: unexpected repair hints or URLs in instruction",
        )
        text = re.sub(r"<!-- harbor-canary GUID [0-9a-f-]+ -->", "", text)
        text, bump_count = re.subn(
            r"^Bumps `[^`]+` from .+ to .+\.$",
            "Bumps <dependency> from <old> to <new>.",
            text,
            flags=re.MULTILINE,
        )
        require(bump_count == 1, f"{task}: expected one normalized bump instruction")
        text = re.sub(r"GitHub URLs for `[^`]+`", "GitHub URLs for <repository>", text)
        templates.add("\n".join(line.strip() for line in text.splitlines() if line.strip()))
    require(len(templates) == 1, "review task instructions use different templates")

    expected = {(configuration, task) for configuration in CONFIGURATIONS for task in task_ids}
    outcome_rows = csv_rows(REVIEW / "results/final_per_task_outcomes.csv")
    outcomes = {(row["configuration"], row["task"]): row for row in outcome_rows}
    require(
        len(outcome_rows) == len(outcomes) == 2030 and set(outcomes) == expected,
        "final outcomes do not cover the exact review matrix",
    )
    per_trial = read_records(REVIEW / "results/per_trial_results.jsonl.gz")
    original = read_records(REVIEW / "results/original_per_trial_results.jsonl.gz")
    require(set(per_trial) == set(original) == expected, "per-trial cohort mismatch")

    for path in (REVIEW / "results").glob("*reruns_203.csv"):
        rows = csv_rows(path)
        require(
            all(row["task"] in task_ids for row in rows),
            f"{path}: rerun provenance contains a task outside the review cohort",
        )
    summary_rows = csv_rows(REVIEW / "results/summary.csv")
    summaries = {f"{row['llm']}__{row['harness']}": row for row in summary_rows}
    require(
        len(summary_rows) == len(summaries) == 10 and set(summaries) == CONFIGURATIONS,
        "result summary configuration mismatch",
    )
    trajectory_rows = csv_rows(REVIEW / "trajectories/index.csv")
    trajectory_index = {f"{row['llm']}__{row['harness']}": row for row in trajectory_rows}
    verifier_rows = csv_rows(REVIEW / "verify_logs/index.csv")
    verifier_index = {f"{row['llm']}__{row['harness']}": row for row in verifier_rows}
    require(
        len(trajectory_rows) == len(verifier_rows) == 10
        and set(trajectory_index) == set(verifier_index) == CONFIGURATIONS,
        "trajectory or verifier index configuration mismatch",
    )
    for directory in ("trajectories", "verify_logs"):
        require(
            {p.name.removesuffix(".jsonl.gz") for p in (REVIEW / directory).glob("*.jsonl.gz")}
            == CONFIGURATIONS,
            f"{directory}: unexpected or missing configuration exports",
        )

    for configuration in sorted(CONFIGURATIONS):
        trajectories = read_records(
            REVIEW / "trajectories" / f"{configuration}.jsonl.gz", trajectories=True
        )
        verifiers = read_records(REVIEW / "verify_logs" / f"{configuration}.jsonl.gz")
        cells = {(configuration, task) for task in task_ids}
        require(set(trajectories) == set(verifiers) == cells, f"{configuration}: cohort mismatch")
        counts = Counter(record["reward"] for record in trajectories.values())
        for key, record in trajectories.items():
            outcome = outcomes[key]
            for other in (verifiers[key], per_trial[key]):
                require(
                    (record["trial"], record["reward"]) == (other["trial"], other["reward"]),
                    f"{key}: selected trial or reward mismatch",
                )
            require(
                record["trial"] == outcome["final_trial"]
                and record["reward"] == reward(outcome["final_reward"]),
                f"{key}: final outcome mismatch",
            )
        summary = summaries[configuration]
        for row in (summary, trajectory_index[configuration], verifier_index[configuration]):
            require(
                tuple(int(row[field]) for field in ("pass", "fail", "no_reward"))
                == (counts[1.0], counts[0.0], counts[None]),
                f"{configuration}: aggregate counts disagree",
            )
        require(
            int(summary["tasks"]) == 203
            and int(summary["with_trajectory"]) == 203
            and int(summary["missing_trajectory"]) == 0
            and abs(float(summary["pass_rate_total"]) - counts[1.0] / 203) < 1e-6,
            f"{configuration}: invalid denominator, coverage, or pass rate",
        )
        require(
            int(trajectory_index[configuration]["rows"]) == 203
            and int(trajectory_index[configuration]["with_trajectory"]) == 203
            and int(trajectory_index[configuration]["missing"]) == 0,
            f"{configuration}: invalid trajectory coverage index",
        )
        require(
            int(verifier_index[configuration]["rows"]) == 203
            and int(verifier_index[configuration]["with_test_stdout"])
            == sum(row["stdout"] for row in verifiers.values())
            and int(verifier_index[configuration]["with_ctrf"])
            == sum(row["ctrf"] for row in verifiers.values()),
            f"{configuration}: invalid verifier coverage index",
        )

    print("Paper-review validation passed: 203 tasks, 10 configurations, 2030 aligned trajectories.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
