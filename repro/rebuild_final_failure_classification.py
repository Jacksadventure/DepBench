#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""Merge failure labels for the final RQ3 non-pass outcomes."""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
FINAL_OUTCOMES = ROOT / "results/final_per_task_outcomes.csv"
OUTPUT_JSONL = ROOT / "analysis/final_failure_classification_203.jsonl"
OUTPUT_COUNTS = ROOT / "analysis/final_failure_category_counts_203.csv"
OUTPUT_SUMMARY = ROOT / "analysis/final_failure_summary_203.json"

CONFIGURATIONS = {
    "gpt55__codex": "codex_gpt55",
    "gpt55__copilot_cli": "copilot_gpt55",
    "gpt55__opencode": "opencode_gpt55",
    "gemini35flash__copilot_cli": "copilot_gemini",
}
REVERSE_CONFIGURATIONS = {
    paper: configuration
    for configuration, paper in CONFIGURATIONS.items()
}
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
AFFECTED_FILES = {
    "gpt55__codex": "failure_labels_gpt55__codex.jsonl",
    "gpt55__copilot_cli": "failure_labels_gpt55__copilot_cli.jsonl",
    "gpt55__opencode": "failure_labels_gpt55__opencode.jsonl",
    "gemini35flash__copilot_cli": (
        "failure_labels_gemini35flash__copilot_cli.jsonl"
    ),
}


def jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def normalized_llm(value: Any) -> str:
    compact = re.sub(r"[^a-z0-9]", "", str(value or "").lower())
    if "gpt55" in compact:
        return "gpt55"
    if "gemini35flash" in compact:
        return "gemini35flash"
    return ""


def annotation_configuration(row: dict[str, Any]) -> str:
    annotation = row.get("annotation") or {}
    llm = normalized_llm(row.get("llm") or annotation.get("llm"))
    harness = str(
        row.get("harness") or annotation.get("harness") or ""
    ).replace("-", "_")
    return f"{llm}__{harness}" if llm and harness else ""


def confidence(value: Any) -> str:
    normalized = str(value or "medium").lower()
    return {"med": "medium"}.get(normalized, normalized)


def load_legacy(
    annotation_root: Path,
) -> dict[str, dict[tuple[str, str], dict[str, Any]]]:
    annotations = {}
    for annotator in ("codex", "opencode"):
        rows = {}
        for row in jsonl(annotation_root / f"{annotator}.jsonl"):
            configuration = annotation_configuration(row)
            annotation = row.get("annotation") or {}
            failure = annotation.get("failure") or {}
            category = failure.get("failure_category_primary")
            if configuration not in CONFIGURATIONS or not category:
                continue
            discovery = annotation.get("discovery") or {}
            rows[(configuration, row["task"])] = {
                "category": category,
                "confidence": confidence(failure.get("confidence")),
                "rationale": failure.get("diagnosis") or (
                    failure.get("proximate_error") or "Legacy failure label."
                ),
                "evidence_source": "legacy_trajectory_annotation",
                "annotator": annotation.get("annotator") or annotator,
                "visible_then_hidden_overfit": bool(
                    discovery.get("visible_then_hidden_overfit")
                ),
            }
        annotations[annotator] = rows
    return annotations


def keyed_paper_rows(
    path: Path,
    include_trial: bool,
) -> dict[tuple[str, ...], dict[str, Any]]:
    rows = {}
    for row in jsonl(path):
        configuration = REVERSE_CONFIGURATIONS.get(row["configuration"])
        if configuration is None:
            continue
        key: tuple[str, ...] = (configuration, row["task"])
        if include_trial:
            key = (*key, row["trial"])
        rows[key] = row
    return rows


def load_affected(path: Path) -> dict[tuple[str, str, str], dict[str, Any]]:
    rows = {}
    for configuration, filename in AFFECTED_FILES.items():
        for row in jsonl(path / filename):
            task = row["task_name"].split("/")[-1]
            key = (configuration, task, row["trial_name"])
            if key in rows:
                raise SystemExit(f"duplicate affected failure label: {key}")
            evidence = row.get("evidence_source", "")
            if isinstance(evidence, list):
                row["evidence_source"] = "; ".join(str(item) for item in evidence)
            rows[key] = row
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--legacy-annotation-root", type=Path, required=True)
    parser.add_argument("--paper-analysis", type=Path, required=True)
    parser.add_argument("--affected-analysis", type=Path, required=True)
    args = parser.parse_args()

    legacy = load_legacy(args.legacy_annotation_root)
    adjudication = keyed_paper_rows(
        args.paper_analysis / "failure_category_adjudication_203.jsonl",
        include_trial=False,
    )
    runtime = keyed_paper_rows(
        args.paper_analysis
        / "runtime_exception_rerun_failure_classification_203.jsonl",
        include_trial=True,
    )
    affected = load_affected(args.affected_analysis)

    outcomes = [
        row
        for row in csv.DictReader(FINAL_OUTCOMES.open(encoding="utf-8"))
        if row["configuration"] in CONFIGURATIONS
        and row["final_reward"] != "1.0"
    ]
    output = []
    for outcome in outcomes:
        configuration = outcome["configuration"]
        task = outcome["task"]
        trial = outcome["final_trial"]
        source = outcome["outcome_source"]
        key = (configuration, task)

        if source == "affected_contract_rerun":
            label = affected[(configuration, task, trial)]
            normalized = {
                "category": label["category"],
                "confidence": confidence(label["confidence"]),
                "rationale": label["rationale"],
                "evidence_source": label["evidence_source"],
                "annotator": label["annotator"],
                "visible_then_hidden_overfit": bool(
                    label["visible_then_hidden_overfit"]
                ),
            }
            classification_source = "affected_contract_rerun_annotation"
        elif source == "targeted_rerun":
            label = runtime[(configuration, task, trial)]
            normalized = {
                "category": label["category"],
                "confidence": confidence(label["confidence"]),
                "rationale": label["rationale"],
                "evidence_source": label["evidence_source"],
                "annotator": label.get("annotator", "runtime-rerun-review"),
                "visible_then_hidden_overfit": bool(
                    label.get("visible_then_hidden_overfit", False)
                ),
            }
            classification_source = "targeted_rerun_annotation"
        elif source == "original_full_run" and key in adjudication:
            label = adjudication[key]
            legacy_overfit = any(
                bool(
                    legacy[name]
                    .get(key, {})
                    .get("visible_then_hidden_overfit", False)
                )
                for name in ("codex", "opencode")
            )
            normalized = {
                "category": label["category"],
                "confidence": confidence(label["confidence"]),
                "rationale": label["rationale"],
                "evidence_source": label["evidence_source"],
                "annotator": "failure-adjudication",
                "visible_then_hidden_overfit": legacy_overfit,
            }
            classification_source = "original_failure_adjudication"
        elif source == "original_full_run":
            labels = [
                legacy[name].get(key) for name in ("codex", "opencode")
            ]
            labels = [label for label in labels if label is not None]
            if not labels or len({label["category"] for label in labels}) != 1:
                raise SystemExit(
                    f"missing or disagreeing legacy failure label: {key}"
                )
            normalized = dict(labels[0])
            normalized["annotator"] = "legacy-consensus"
            normalized["visible_then_hidden_overfit"] = any(
                label["visible_then_hidden_overfit"] for label in labels
            )
            classification_source = "original_annotation_consensus"
        else:
            raise SystemExit(
                f"unsupported final failure source for {key}: {source}"
            )

        if normalized["category"] not in CATEGORIES:
            raise SystemExit(
                f"unknown failure category for {key}: "
                f"{normalized['category']}"
            )
        output.append(
            {
                "configuration": configuration,
                "paper_configuration": CONFIGURATIONS[configuration],
                "task": task,
                "trial": trial,
                "category": normalized["category"],
                "confidence": normalized["confidence"],
                "rationale": normalized["rationale"],
                "evidence_source": normalized["evidence_source"],
                "annotator": normalized["annotator"],
                "visible_then_hidden_overfit": normalized[
                    "visible_then_hidden_overfit"
                ],
                "outcome_source": source,
                "classification_source": classification_source,
            }
        )

    output.sort(
        key=lambda row: (
            row["configuration"],
            row["task"],
            row["trial"],
        )
    )
    keys = {
        (row["configuration"], row["task"], row["trial"]) for row in output
    }
    if len(output) != 477 or len(keys) != 477:
        raise SystemExit(
            f"expected 477 unique final failure labels, got {len(output)}"
        )

    with OUTPUT_JSONL.open("w", encoding="utf-8") as handle:
        for row in output:
            handle.write(
                json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n"
            )

    by_configuration = {
        configuration: Counter(
            row["category"]
            for row in output
            if row["configuration"] == configuration
        )
        for configuration in CONFIGURATIONS
    }
    with OUTPUT_COUNTS.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["category", *CONFIGURATIONS, "total"],
            lineterminator="\n",
        )
        writer.writeheader()
        for category in CATEGORIES:
            values = {
                configuration: by_configuration[configuration][category]
                for configuration in CONFIGURATIONS
            }
            writer.writerow(
                {
                    "category": category,
                    **values,
                    "total": sum(values.values()),
                }
            )

    source_counts = Counter(row["classification_source"] for row in output)
    summary = {
        "cells": len(output),
        "configurations": {
            configuration: {
                "non_passes": sum(by_configuration[configuration].values()),
                "category_counts": {
                    category: by_configuration[configuration][category]
                    for category in CATEGORIES
                },
            }
            for configuration in CONFIGURATIONS
        },
        "category_counts": {
            category: sum(
                by_configuration[configuration][category]
                for configuration in CONFIGURATIONS
            )
            for category in CATEGORIES
        },
        "classification_sources": dict(sorted(source_counts.items())),
    }
    OUTPUT_SUMMARY.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print("merged 477 final non-pass failure classifications")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
