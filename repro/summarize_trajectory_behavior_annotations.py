#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""Validate and summarize final trajectory behavior annotations."""

from __future__ import annotations

import csv
import gzip
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANNOTATION_PATH = ROOT / "analysis/trajectory_behavior_annotations_203.jsonl"
SUMMARY_CSV_PATH = ROOT / "analysis/trajectory_behavior_summary_203.csv"
SOURCE_CSV_PATH = ROOT / "analysis/trajectory_behavior_by_source_203.csv"
SUMMARY_JSON_PATH = ROOT / "analysis/trajectory_behavior_summary_203.json"

BEHAVIORS = (
    "docs_lookup",
    "api_source_inspection",
    "ran_tests",
    "bc_hypothesis",
)


def final_trajectory_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted((ROOT / "trajectories").glob("*.jsonl.gz")):
        configuration = path.name.removesuffix(".jsonl.gz")
        with gzip.open(path, "rt", encoding="utf-8") as handle:
            for line in handle:
                row = json.loads(line)
                rows.append(
                    {
                        "configuration": configuration,
                        "task": row["task"],
                        "trial": row["trial"],
                        "outcome_source": row.get("outcome_source", ""),
                        "passed": float(row.get("reward") or 0) == 1.0,
                    }
                )
    return rows


def load_annotations() -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in ANNOTATION_PATH.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def validate(
    final_rows: list[dict[str, Any]],
    annotations: list[dict[str, Any]],
) -> None:
    expected = {
        (row["configuration"], row["task"], row["trial"])
        for row in final_rows
    }
    actual = {
        (row["configuration"], row["task"], row["trial"])
        for row in annotations
    }
    if len(final_rows) != 2030 or len(expected) != 2030:
        raise SystemExit("expected 2,030 unique final trajectory rows")
    if len(annotations) != 2030 or len(actual) != 2030:
        raise SystemExit("expected 2,030 unique behavior annotations")
    if actual != expected:
        raise SystemExit(
            "behavior annotation coverage mismatch: "
            f"missing={len(expected - actual)} extra={len(actual - expected)}"
        )
    for behavior in BEHAVIORS:
        if any(
            not isinstance(row.get(behavior), bool) for row in annotations
        ):
            raise SystemExit(f"{behavior} must be boolean in every annotation")
    for field in ("annotation_source", "annotator"):
        if any(
            not isinstance(row.get(field), str) or not row[field]
            for row in annotations
        ):
            raise SystemExit(f"{field} is required in every annotation")


def summarize_groups(
    rows: list[dict[str, Any]],
    group_fields: tuple[str, ...],
) -> list[dict[str, Any]]:
    keys = sorted({tuple(row[field] for field in group_fields) for row in rows})
    summary = []
    for key in keys:
        subset = [
            row
            for row in rows
            if tuple(row[field] for field in group_fields) == key
        ]
        record = dict(zip(group_fields, key))
        record["rows"] = len(subset)
        record["passes"] = sum(row["passed"] for row in subset)
        record["non_passes"] = len(subset) - record["passes"]
        for behavior in BEHAVIORS:
            record[behavior] = sum(row[behavior] for row in subset)
        summary.append(record)
    return summary


def write_csv(
    path: Path,
    rows: list[dict[str, Any]],
    group_fields: tuple[str, ...],
) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                *group_fields,
                "rows",
                "passes",
                "non_passes",
                *BEHAVIORS,
            ],
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    final_rows = final_trajectory_rows()
    annotations = load_annotations()
    validate(final_rows, annotations)
    source_by_key = {
        (row["configuration"], row["task"], row["trial"]): row
        for row in final_rows
    }
    for row in annotations:
        source = source_by_key[
            (row["configuration"], row["task"], row["trial"])
        ]
        row["outcome_source"] = source["outcome_source"]
        row["passed"] = source["passed"]

    summary = summarize_groups(annotations, ("configuration",))
    by_source = summarize_groups(
        annotations, ("configuration", "outcome_source")
    )
    write_csv(SUMMARY_CSV_PATH, summary, ("configuration",))
    write_csv(
        SOURCE_CSV_PATH,
        by_source,
        ("configuration", "outcome_source"),
    )

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "method": (
            "One behavior annotation per final trajectory using the repository "
            "trajectory-annotation schema; original labels are retained when "
            "the final trial is unchanged and replacement trials are annotated "
            "with the same definitions."
        ),
        "behaviors": list(BEHAVIORS),
        "summary": summary,
        "summary_by_source": by_source,
        "annotation_sources": dict(
            sorted(Counter(row["annotation_source"] for row in annotations).items())
        ),
        "annotators": dict(
            sorted(Counter(row["annotator"] for row in annotations).items())
        ),
    }
    SUMMARY_JSON_PATH.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print("validated and summarized 2,030 final trajectory annotations")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
