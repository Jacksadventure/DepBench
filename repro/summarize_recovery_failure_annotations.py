#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""Validate and summarize trajectory-recovery non-pass annotations."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANNOTATION_PATH = (
    ROOT / "analysis/trajectory_recovery_failure_classification_203.jsonl"
)
COUNTS_PATH = (
    ROOT / "analysis/trajectory_recovery_failure_category_counts_203.csv"
)
SUMMARY_PATH = (
    ROOT / "analysis/trajectory_recovery_failure_summary_203.json"
)
FINAL_OUTCOMES_PATH = ROOT / "results/final_per_task_outcomes.csv"

CATEGORIES = (
    "incomplete-migration",
    "wrong-root-cause",
    "wrong-semantic-output",
    "infra-exception",
    "gave-up-or-budget",
    "no-upgrade-attempted",
    "compile-namespace-inconsistency",
    "install-build-failure",
    "test-tampering",
)


def reward_is_pass(value: str) -> bool:
    return value != "" and float(value) == 1.0


def expected_annotation_keys() -> set[tuple[str, str, str]]:
    return {
        (row["configuration"], row["task"], row["final_trial"])
        for row in csv.DictReader(FINAL_OUTCOMES_PATH.open(encoding="utf-8"))
        if row["outcome_source"] == "trajectory_recovery_rerun"
        and not reward_is_pass(row["final_reward"])
    }


def load_annotations() -> list[dict[str, Any]]:
    rows = []
    for line in ANNOTATION_PATH.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def validate_annotations(rows: list[dict[str, Any]]) -> None:
    expected = expected_annotation_keys()
    actual = {
        (row["configuration"], row["task"], row["trial"]) for row in rows
    }
    if len(rows) != len(actual):
        raise SystemExit("trajectory-recovery annotations contain duplicates")
    if actual != expected:
        raise SystemExit(
            "trajectory-recovery annotation coverage does not match non-passes: "
            f"missing={len(expected - actual)} extra={len(actual - expected)}"
        )
    if len(rows) != len(expected):
        raise SystemExit(
            f"expected {len(expected)} annotations, got {len(rows)}"
        )
    unknown = sorted({row["category"] for row in rows} - set(CATEGORIES))
    if unknown:
        raise SystemExit(f"unknown trajectory-recovery categories: {unknown}")
    if any(
        row["confidence"] not in {"high", "medium", "low"} for row in rows
    ):
        raise SystemExit("unknown trajectory-recovery confidence value")
    if any(
        not isinstance(row["visible_then_hidden_overfit"], bool) for row in rows
    ):
        raise SystemExit("visible_then_hidden_overfit must be boolean")
    for field in ("rationale", "evidence_source", "annotator"):
        if any(not isinstance(row.get(field), str) or not row[field] for row in rows):
            raise SystemExit(f"trajectory-recovery annotations require {field}")


def main() -> int:
    rows = load_annotations()
    required_fields = {
        "configuration",
        "task",
        "trial",
        "category",
        "confidence",
        "rationale",
        "evidence_source",
        "annotator",
        "visible_then_hidden_overfit",
    }
    for index, row in enumerate(rows, start=1):
        missing = required_fields - set(row)
        if missing:
            raise SystemExit(
                f"trajectory-recovery annotation {index} is missing "
                f"{sorted(missing)}"
            )
    expected = expected_annotation_keys()
    rows = [
        row
        for row in rows
        if (row["configuration"], row["task"], row["trial"]) in expected
    ]
    validate_annotations(rows)
    with ANNOTATION_PATH.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(
                json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n"
            )
    configurations = sorted({row["configuration"] for row in rows})
    by_configuration = {
        configuration: Counter(
            row["category"]
            for row in rows
            if row["configuration"] == configuration
        )
        for configuration in configurations
    }

    with COUNTS_PATH.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["category", *configurations, "total"],
            lineterminator="\n",
        )
        writer.writeheader()
        for category in CATEGORIES:
            values = {
                configuration: by_configuration[configuration][category]
                for configuration in configurations
            }
            writer.writerow(
                {
                    "category": category,
                    **values,
                    "total": sum(values.values()),
                }
            )

    total_categories = Counter(row["category"] for row in rows)
    total_confidence = Counter(row["confidence"] for row in rows)
    total_annotators = Counter(row["annotator"] for row in rows)
    total_overfit = sum(row["visible_then_hidden_overfit"] for row in rows)
    summary = {
        "cells": len(rows),
        "category_counts": {
            category: total_categories[category] for category in CATEGORIES
        },
        "confidence_counts": {
            confidence: total_confidence[confidence]
            for confidence in ("high", "medium", "low")
        },
        "annotator_counts": dict(sorted(total_annotators.items())),
        "visible_then_hidden_overfit": total_overfit,
        "visible_then_hidden_overfit_share": round(total_overfit / len(rows), 4),
        "by_configuration": {},
    }
    for configuration in configurations:
        subset = [
            row for row in rows if row["configuration"] == configuration
        ]
        confidence = Counter(row["confidence"] for row in subset)
        annotators = Counter(row["annotator"] for row in subset)
        overfit = sum(row["visible_then_hidden_overfit"] for row in subset)
        summary["by_configuration"][configuration] = {
            "cells": len(subset),
            "category_counts": {
                category: by_configuration[configuration][category]
                for category in CATEGORIES
            },
            "confidence_counts": {
                value: confidence[value]
                for value in ("high", "medium", "low")
            },
            "annotator_counts": dict(sorted(annotators.items())),
            "visible_then_hidden_overfit": overfit,
            "visible_then_hidden_overfit_share": round(
                overfit / len(subset), 4
            ),
        }

    SUMMARY_PATH.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        f"validated {len(rows)} trajectory-recovery non-passes across "
        f"{len(configurations)} configurations"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
