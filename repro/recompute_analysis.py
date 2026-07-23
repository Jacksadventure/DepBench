#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""Recompute result-derived analysis after final-trial replacement."""

from __future__ import annotations

import csv
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SUMMARY_PATH = ROOT / "analysis/runtime_exception_rerun_summary_203.json"
PAPER_NUMBERS_PATH = ROOT / "analysis/paper_numbers_203.json"
RECOVERY_FAILURE_SUMMARY_PATH = (
    ROOT / "analysis/trajectory_recovery_failure_summary_203.json"
)


def reward_is_pass(value: str) -> bool:
    return value != "" and float(value) == 1.0


def load_outcomes() -> list[dict[str, str]]:
    return list(
        csv.DictReader(
            (ROOT / "results/final_per_task_outcomes.csv").open(
                encoding="utf-8"
            )
        )
    )


def pass_maps(
    outcomes: list[dict[str, str]],
) -> dict[str, dict[str, bool]]:
    maps: dict[str, dict[str, bool]] = {}
    for row in outcomes:
        maps.setdefault(row["configuration"], {})[row["task"]] = reward_is_pass(
            row["final_reward"]
        )
    return maps


def overlap_analysis(
    maps: dict[str, dict[str, bool]],
    ecosystems: dict[str, str],
) -> tuple[dict[str, Any], dict[str, dict[str, int]]]:
    overlap: dict[str, Any] = {}
    totals: dict[str, dict[str, int]] = {}
    llms = sorted({configuration.split("__", 1)[0] for configuration in maps})
    for llm in llms:
        configurations = sorted(
            configuration
            for configuration in maps
            if configuration.startswith(f"{llm}__")
        )
        overlap[llm] = {}
        total_counts = Counter()
        for ecosystem in sorted(set(ecosystems.values())):
            tasks = sorted(
                task
                for task, task_ecosystem in ecosystems.items()
                if task_ecosystem == ecosystem
            )
            counts = Counter()
            for task in tasks:
                passes = sum(maps[configuration][task] for configuration in configurations)
                if passes == 0:
                    counts["zero"] += 1
                elif passes == len(configurations):
                    counts["all"] += 1
                else:
                    counts["partial"] += 1
            overlap[llm][ecosystem] = {
                key: counts[key]
                for key in ("zero", "partial", "all")
                if counts[key]
            }
            total_counts.update(counts)
        totals[llm] = {
            "harnesses": len(configurations),
            "zero": total_counts["zero"],
            "partial": total_counts["partial"],
            "all": total_counts["all"],
        }
    return overlap, totals


def recovery_summary() -> dict[str, Any]:
    path = ROOT / "results/trajectory_recovery_reruns_203.csv"
    if not path.exists():
        return {"cells": 0, "by_configuration": {}}
    rows = list(csv.DictReader(path.open(encoding="utf-8")))
    by_configuration: dict[str, Counter] = {}
    for row in rows:
        counter = by_configuration.setdefault(row["configuration"], Counter())
        counter["cells"] += 1
        counter["pass" if reward_is_pass(row["reward"]) else "non_pass"] += 1
        if row["exception_type"]:
            counter["exception"] += 1
    return {
        "cells": len(rows),
        "pass": sum(reward_is_pass(row["reward"]) for row in rows),
        "non_pass": sum(not reward_is_pass(row["reward"]) for row in rows),
        "exception": sum(bool(row["exception_type"]) for row in rows),
        "by_configuration": {
            configuration: dict(counter)
            for configuration, counter in sorted(by_configuration.items())
        },
    }


def trajectory_behavior_by_source() -> dict[str, dict[str, dict[str, int]]]:
    rows = list(
        csv.DictReader(
            (ROOT / "analysis/trajectory_behavior_by_source_203.csv").open(
                encoding="utf-8"
            )
        )
    )
    result: dict[str, dict[str, dict[str, int]]] = {}
    for row in rows:
        result.setdefault(row["configuration"], {})[row["outcome_source"]] = {
            "rows": int(row["rows"]),
            "passes": int(row["passes"]),
            "non_passes": int(row["non_passes"]),
            "with_trajectory": int(row["rows"]),
            "docs_lookup": int(row["docs_lookup"]),
            "dependency_api_lookup": int(row["api_source_inspection"]),
            "test_or_build_feedback": int(row["ran_tests"]),
            "breaking_change_reasoning": int(row["bc_hypothesis"]),
        }
    return result


def main() -> int:
    outcomes = load_outcomes()
    maps = pass_maps(outcomes)
    task_summary = json.loads(
        (ROOT / "dataset/task_summary.json").read_text(encoding="utf-8")
    )
    ecosystems = {row["folder"]: row["ecosystem"] for row in task_summary}

    pass_counts = {
        configuration: sum(task_results.values())
        for configuration, task_results in sorted(maps.items())
    }
    ecosystem_pass_counts: dict[str, dict[str, int]] = {}
    for configuration, task_results in sorted(maps.items()):
        counts = Counter(
            ecosystems[task]
            for task, passed in task_results.items()
            if passed
        )
        ecosystem_pass_counts[configuration] = {
            ecosystem: counts[ecosystem]
            for ecosystem in sorted(set(ecosystems.values()))
        }

    overlap, overlap_totals = overlap_analysis(maps, ecosystems)
    trajectory_behavior = list(
        csv.DictReader(
            (ROOT / "analysis/trajectory_behavior_summary_203.csv").open(
                encoding="utf-8"
            )
        )
    )

    document = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))
    document["pass_counts"] = pass_counts
    document["ecosystem_pass_counts"] = ecosystem_pass_counts
    document["pass_overlap"] = overlap
    document["gpt55_zero_pass_total"] = overlap_totals["gpt55"]["zero"]
    document["gpt55_all_pass_total"] = overlap_totals["gpt55"]["all"]
    document["trajectory_recovery_rerun"] = recovery_summary()
    document["trajectory_recovery_failure_analysis"] = json.loads(
        RECOVERY_FAILURE_SUMMARY_PATH.read_text(encoding="utf-8")
    )
    document["final_trajectory_scan_by_source"] = (
        trajectory_behavior_by_source()
    )
    document["final_trajectory_scan"] = {
        row["configuration"]: {
            "rows": int(row["rows"]),
            "with_trajectory": int(row["rows"]),
            "docs_lookup": int(row["docs_lookup"]),
            "dependency_api_lookup": int(row["api_source_inspection"]),
            "test_or_build_feedback": int(row["ran_tests"]),
            "breaking_change_reasoning": int(row["bc_hypothesis"]),
        }
        for row in trajectory_behavior
    }
    SUMMARY_PATH.write_text(
        json.dumps(document, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    paper_numbers = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "benchmark_tasks": len(ecosystems),
        "pass_counts": pass_counts,
        "non_pass_counts": {
            configuration: len(task_results) - sum(task_results.values())
            for configuration, task_results in sorted(maps.items())
        },
        "ecosystem_pass_counts": ecosystem_pass_counts,
        "pass_overlap": overlap,
        "pass_overlap_totals": overlap_totals,
        "final_trajectory_scan": document["final_trajectory_scan"],
        "final_trajectory_scan_by_source": document[
            "final_trajectory_scan_by_source"
        ],
        "trajectory_recovery_rerun": document["trajectory_recovery_rerun"],
        "trajectory_recovery_failure_analysis": document[
            "trajectory_recovery_failure_analysis"
        ],
    }
    PAPER_NUMBERS_PATH.write_text(
        json.dumps(paper_numbers, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        "recomputed pass counts, ecosystem counts, overlap regimes, and "
        "trajectory behavior, provenance, and recovery failure analysis"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
