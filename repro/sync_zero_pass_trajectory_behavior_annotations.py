#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""Replace behavior labels for zero-pass contract-repair trajectories."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANNOTATIONS = ROOT / "analysis/trajectory_behavior_annotations_203.jsonl"
SCAN_DETAIL = ROOT / "analysis/trajectory_scan_detail.csv"
FINAL_OUTCOMES = ROOT / "results/final_per_task_outcomes.csv"


def main() -> int:
    final_rows = list(csv.DictReader(FINAL_OUTCOMES.open(encoding="utf-8")))
    repaired = {
        (row["configuration"], row["task"], row["final_trial"])
        for row in final_rows
        if row["outcome_source"] == "zero_pass_contract_repair_rerun"
    }
    if len(repaired) != 200:
        raise SystemExit(
            f"expected 200 zero-pass contract-repair final cells, "
            f"got {len(repaired)}"
        )

    old_rows = [
        json.loads(line)
        for line in ANNOTATIONS.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    final_cells = {
        (row["configuration"], row["task"]) for row in final_rows
    }
    replaced_cells = {
        (configuration, task)
        for configuration, task, _ in repaired
    }
    preserved = [
        row
        for row in old_rows
        if (row["configuration"], row["task"]) not in replaced_cells
    ]
    if len(preserved) != 1830:
        raise SystemExit(
            f"expected 1,830 preserved behavior rows, got {len(preserved)}"
        )

    scan_rows = list(csv.DictReader(SCAN_DETAIL.open(encoding="utf-8")))
    scan_by_key = {
        (row["configuration"], row["task"], row["trial"]): row
        for row in scan_rows
    }
    if not repaired <= set(scan_by_key):
        raise SystemExit(
            f"trajectory scan is missing "
            f"{len(repaired - set(scan_by_key))} repaired rows"
        )

    def boolean(row: dict[str, str], field: str) -> bool:
        value = row[field].strip().lower()
        if value not in {"true", "false"}:
            raise SystemExit(f"{field} is not boolean text: {value!r}")
        return value == "true"

    generated = []
    for configuration, task, trial in sorted(repaired):
        scan = scan_by_key[(configuration, task, trial)]
        generated.append(
            {
                "configuration": configuration,
                "task": task,
                "trial": trial,
                "docs_lookup": boolean(scan, "docs_lookup"),
                "api_source_inspection": boolean(
                    scan, "dependency_api_lookup"
                ),
                "ran_tests": boolean(scan, "test_or_build_feedback"),
                "bc_hypothesis": boolean(
                    scan, "breaking_change_reasoning"
                ),
                "confidence": "medium",
                "rationale": (
                    "Rule-based scan of the final zero-pass contract-repair "
                    "trajectory using the release behavior definitions."
                ),
                "annotation_source": (
                    "zero_pass_contract_repair_rule_scan"
                ),
                "annotator": "rule-scan-20260731",
            }
        )

    output = sorted(
        [*preserved, *generated],
        key=lambda row: (
            row["configuration"],
            row["task"],
            row["trial"],
        ),
    )
    keys = {
        (row["configuration"], row["task"], row["trial"]) for row in output
    }
    if len(output) != 2030 or len(keys) != 2030:
        raise SystemExit("expected 2,030 unique final behavior annotations")
    if {(configuration, task) for configuration, task, _ in keys} != final_cells:
        raise SystemExit("behavior annotations do not cover the final cells")

    with ANNOTATIONS.open("w", encoding="utf-8") as handle:
        for row in output:
            handle.write(
                json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n"
            )
    print(
        "preserved 1,830 labels and generated 200 zero-pass repair labels"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
