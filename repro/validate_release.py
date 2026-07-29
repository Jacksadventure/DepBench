#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

from __future__ import annotations

import csv
import gzip
import hashlib
import io
import json
import tarfile
from collections import Counter
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parents[1]
CONFIGURATIONS = {
    "claude48__claude_code",
    "claude48__copilot_cli",
    "claude48__opencode",
    "gemini35flash__claude_code",
    "gemini35flash__copilot_cli",
    "gemini35flash__opencode",
    "gpt55__claude_code",
    "gpt55__codex",
    "gpt55__copilot_cli",
    "gpt55__opencode",
}
JOB_CONFIGURATIONS = {
    "claude_code__claude48": "claude48__claude_code",
    "claude_code__gemini35flash": "gemini35flash__claude_code",
    "claude_code__gpt55": "gpt55__claude_code",
    "codex__gpt55": "gpt55__codex",
    "copilot_cli__claude48": "claude48__copilot_cli",
    "copilot_cli__gemini35flash": "gemini35flash__copilot_cli",
    "copilot_cli__gpt55": "gpt55__copilot_cli",
    "opencode__claude48": "claude48__opencode",
    "opencode__gemini35flash": "gemini35flash__opencode",
    "opencode__gpt55": "gpt55__opencode",
}
ENVIRONMENT_REPAIR_TASKS = {
    "MystenLabs__fastcrypto__460",
    "OpenRefine__OpenRefine__7503",
    "Stranger6667__jsonschema__825",
    "dadoonet__fscrawler__2342",
    "elastic__apm-agent-java__2792",
    "geotools__geotools__4212",
    "imsnif__bandwhich__430",
    "matsim-org__matsim-libs__2586",
    "mike-engel__jwt-cli__214",
    "mike-engel__jwt-cli__224",
    "mitmproxy__mitmproxy_rs__142",
    "mozilla__sccache__1190",
    "omjadas__hudsucker__88",
    "onthegomap__planetiler__685",
    "oxidecomputer__dropshot__501",
    "oxidecomputer__dropshot__630",
    "prometheus__client_java__1402",
    "rash-sh__rash__698",
    "regexident__cargo-modules__122",
    "regexident__cargo-modules__389",
    "scx567888__live-room-watcher__209",
    "smol-rs__async-lock__69",
    "talsma-ict__umldoclet__709",
    "ymtdzzz__otel-tui__153",
}


def count_gzip_jsonl(path: Path) -> int:
    count = 0
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        for line in handle:
            json.loads(line)
            count += 1
    return count


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def result_reward(result: dict) -> float:
    value = (
        ((result.get("verifier_result") or {}).get("rewards") or {}).get(
            "reward"
        )
    )
    return 0.0 if value is None else float(value)


def main() -> int:
    task_summary_path = ROOT / "dataset/task_summary.json"
    tasks_path = ROOT / "dataset/tasks"
    if not task_summary_path.is_file() or not tasks_path.is_dir():
        raise SystemExit(
            "benchmark dataset not found; run: python3 repro/download_benchmark.py"
        )

    task_summary = json.loads(task_summary_path.read_text())
    task_dirs = [p for p in tasks_path.iterdir() if p.is_dir()]
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

    manifest = json.loads((ROOT / "MANIFEST.json").read_text())
    if (
        manifest.get("dataset") != "DepBench contract-clean 203"
        or manifest.get("tasks") != 203
        or manifest.get("total_trials") != 2030
        or manifest.get("targeted_rerun_cells") != 46
        or manifest.get("trajectory_recovery_rerun_cells") != 106
        or manifest.get("task_metadata_correction_rerun_cells") != 0
        or manifest.get("affected_contract_rerun_cells") != 530
        or manifest.get("environment_repair_rerun_cells") != 240
    ):
        raise SystemExit("MANIFEST.json does not describe the final release")

    final_outcomes = list(
        csv.DictReader((ROOT / "results/final_per_task_outcomes.csv").open())
    )
    if len(final_outcomes) != 2030:
        raise SystemExit(f"expected 2030 final outcomes, got {len(final_outcomes)}")
    final_cells = {
        (row["configuration"], row["task"]) for row in final_outcomes
    }
    expected_final_cells = {
        (configuration, task)
        for configuration in CONFIGURATIONS
        for task in active_tasks
    }
    if final_cells != expected_final_cells:
        raise SystemExit(
            "final outcomes do not cover the 203-task x 10-configuration matrix"
        )
    if {row["task"] for row in final_outcomes} != active_tasks:
        raise SystemExit("final outcome tasks do not match the release")
    if sum(row["outcome_source"] == "targeted_rerun" for row in final_outcomes) != 46:
        raise SystemExit("expected 46 final targeted rerun outcomes")
    rerun_rows = list(
        csv.DictReader(
            (ROOT / "results/targeted_runtime_exception_reruns_203.csv").open()
        )
    )
    if len(rerun_rows) != 111 or len(
        {(row["configuration"], row["task"]) for row in rerun_rows}
    ) != 111:
        raise SystemExit("expected 111 unique targeted rerun cells")
    recovery_path = ROOT / "results/trajectory_recovery_reruns_203.csv"
    if not recovery_path.exists():
        raise SystemExit("missing trajectory-recovery rerun records")
    recovery_rows = list(csv.DictReader(recovery_path.open()))
    if len(recovery_rows) != 177 or len(
        {(row["configuration"], row["task"]) for row in recovery_rows}
    ) != 177:
        raise SystemExit("expected 177 unique trajectory-recovery rerun cells")
    if (
        sum(
            row["outcome_source"] == "trajectory_recovery_rerun"
            for row in final_outcomes
        )
        != 106
    ):
        raise SystemExit(
            "final outcomes do not contain 106 trajectory-recovery reruns"
        )
    correction_rows = list(
        csv.DictReader(
            (
                ROOT / "results/task_metadata_correction_reruns_203.csv"
            ).open()
        )
    )
    if len(correction_rows) != 10 or len(
        {(row["configuration"], row["task"]) for row in correction_rows}
    ) != 10:
        raise SystemExit("expected 10 unique task-metadata correction reruns")
    if (
        sum(
            row["outcome_source"] == "task_metadata_correction_rerun"
            for row in final_outcomes
        )
        != 0
    ):
        raise SystemExit(
            "final outcomes contain superseded task-metadata correction reruns"
        )

    affected_rows = list(
        csv.DictReader(
            (
                ROOT / "results/affected_contract_reruns_203.csv"
            ).open()
        )
    )
    if len(affected_rows) != 560 or len(
        {(row["configuration"], row["task"]) for row in affected_rows}
    ) != 560:
        raise SystemExit("expected 560 unique affected-contract rerun cells")
    if (
        sum(
            row["outcome_source"] == "affected_contract_rerun"
            for row in final_outcomes
        )
        != 530
    ):
        raise SystemExit(
            "final outcomes do not contain 530 affected-contract reruns"
        )

    environment_rows = list(
        csv.DictReader(
            (
                ROOT / "results/environment_repair_reruns_203.csv"
            ).open()
        )
    )
    environment_cells = {
        (row["configuration"], row["task"]) for row in environment_rows
    }
    expected_environment_cells = {
        (configuration, task)
        for configuration in CONFIGURATIONS
        for task in ENVIRONMENT_REPAIR_TASKS
    }
    if (
        len(environment_rows) != 240
        or environment_cells != expected_environment_cells
    ):
        raise SystemExit(
            "environment-repair reruns do not cover the expected "
            "24-task x 10-configuration matrix"
        )
    final_environment_rows = {
        (row["configuration"], row["task"]): row
        for row in final_outcomes
        if row["outcome_source"] == "environment_repair_rerun"
    }
    if (
        set(final_environment_rows) != expected_environment_cells
    ):
        raise SystemExit(
            "final outcomes do not contain the expected environment-repair cells"
        )
    for row in environment_rows:
        key = (row["configuration"], row["task"])
        final = final_environment_rows[key]
        if (
            final["final_trial"] != row["trial"]
            or final["final_job"] != row["job_name"]
            or final["final_reward"] != row["reward"]
            or final["rerun_exception_type"] != row["exception_type"]
            or final["rerun_exception_message"] != row["exception_message"]
        ):
            raise SystemExit(
                f"{key}: environment provenance does not match final outcome"
            )

    environment_summary = json.loads(
        (
            ROOT / "analysis/environment_repair_rerun_summary_203.json"
        ).read_text(encoding="utf-8")
    )
    expected_environment_summary = {
        "affected_tasks": 24,
        "configurations": 10,
        "trials": 240,
        "pass": sum(row["reward"] == "1.0" for row in environment_rows),
        "non_pass": sum(row["reward"] != "1.0" for row in environment_rows),
    }
    for field, expected in expected_environment_summary.items():
        if environment_summary.get(field) != expected:
            raise SystemExit(
                f"environment summary {field} is stale: "
                f"{environment_summary.get(field)} != {expected}"
            )
    if set(environment_summary.get("by_configuration", {})) != CONFIGURATIONS:
        raise SystemExit(
            "environment summary does not cover all 10 configurations"
        )
    for configuration in CONFIGURATIONS:
        subset = [
            row
            for row in environment_rows
            if row["configuration"] == configuration
        ]
        expected = {
            "trials": 24,
            "pass": sum(row["reward"] == "1.0" for row in subset),
            "non_pass": sum(row["reward"] != "1.0" for row in subset),
            "exceptions": dict(
                sorted(
                    Counter(
                        row["exception_type"] or "none" for row in subset
                    ).items()
                )
            ),
        }
        if environment_summary["by_configuration"][configuration] != expected:
            raise SystemExit(
                f"{configuration}: environment summary is stale"
            )

    recovery_annotations = [
        json.loads(line)
        for line in (
            ROOT
            / "analysis/trajectory_recovery_failure_classification_203.jsonl"
        )
        .read_text(encoding="utf-8")
        .splitlines()
        if line.strip()
    ]
    expected_recovery_non_passes = {
        (row["configuration"], row["task"], row["final_trial"])
        for row in final_outcomes
        if row["outcome_source"] == "trajectory_recovery_rerun"
        and row["final_reward"] != "1.0"
    }
    observed_recovery_non_passes = {
        (row["configuration"], row["task"], row["trial"])
        for row in recovery_annotations
    }
    if (
        len(recovery_annotations) != len(expected_recovery_non_passes)
        or len(observed_recovery_non_passes)
        != len(expected_recovery_non_passes)
        or observed_recovery_non_passes != expected_recovery_non_passes
    ):
        raise SystemExit(
            "trajectory-recovery annotations do not cover all final non-passes"
        )
    if manifest.get("trajectory_recovery_non_pass_annotations") != len(
        expected_recovery_non_passes
    ):
        raise SystemExit(
            "MANIFEST trajectory-recovery annotation count is stale"
        )
    recovery_categories = [
        "incomplete-migration",
        "wrong-root-cause",
        "wrong-semantic-output",
        "infra-exception",
        "gave-up-or-budget",
        "no-upgrade-attempted",
        "compile-namespace-inconsistency",
        "install-build-failure",
        "test-tampering",
    ]
    recovery_configurations = sorted(
        {row["configuration"] for row in recovery_annotations}
    )
    recovery_by_configuration = {
        configuration: Counter(
            row["category"]
            for row in recovery_annotations
            if row["configuration"] == configuration
        )
        for configuration in recovery_configurations
    }
    recovery_count_rows = list(
        csv.DictReader(
            (
                ROOT
                / "analysis/trajectory_recovery_failure_category_counts_203.csv"
            ).open(encoding="utf-8")
        )
    )
    if [row["category"] for row in recovery_count_rows] != recovery_categories:
        raise SystemExit("trajectory-recovery failure counts are stale")
    for row in recovery_count_rows:
        category = row["category"]
        expected_total = 0
        for configuration in recovery_configurations:
            expected = recovery_by_configuration[configuration][category]
            if int(row[configuration]) != expected:
                raise SystemExit(
                    f"{configuration}/{category}: recovery failure count "
                    "is stale"
                )
            expected_total += expected
        if int(row["total"]) != expected_total:
            raise SystemExit(
                f"{category}: recovery failure total is stale"
            )

    recovery_summary = json.loads(
        (
            ROOT / "analysis/trajectory_recovery_failure_summary_203.json"
        ).read_text(encoding="utf-8")
    )
    recovery_total_categories = Counter(
        row["category"] for row in recovery_annotations
    )
    recovery_total_confidence = Counter(
        row["confidence"] for row in recovery_annotations
    )
    recovery_total_annotators = Counter(
        row["annotator"] for row in recovery_annotations
    )
    recovery_total_overfit = sum(
        row["visible_then_hidden_overfit"]
        for row in recovery_annotations
    )
    expected_recovery_summary = {
        "cells": len(recovery_annotations),
        "category_counts": {
            category: recovery_total_categories[category]
            for category in recovery_categories
        },
        "confidence_counts": {
            confidence: recovery_total_confidence[confidence]
            for confidence in ("high", "medium", "low")
        },
        "annotator_counts": dict(
            sorted(recovery_total_annotators.items())
        ),
        "visible_then_hidden_overfit": recovery_total_overfit,
        "visible_then_hidden_overfit_share": round(
            recovery_total_overfit / len(recovery_annotations), 4
        ),
        "by_configuration": {},
    }
    for configuration in recovery_configurations:
        subset = [
            row
            for row in recovery_annotations
            if row["configuration"] == configuration
        ]
        confidence = Counter(row["confidence"] for row in subset)
        annotators = Counter(row["annotator"] for row in subset)
        overfit = sum(
            row["visible_then_hidden_overfit"] for row in subset
        )
        expected_recovery_summary["by_configuration"][configuration] = {
            "cells": len(subset),
            "category_counts": {
                category: recovery_by_configuration[configuration][category]
                for category in recovery_categories
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
    if recovery_summary != expected_recovery_summary:
        raise SystemExit(
            "trajectory-recovery failure summary is stale"
        )

    rq3_configurations = {
        "gpt55__codex",
        "gpt55__copilot_cli",
        "gpt55__opencode",
        "gemini35flash__copilot_cli",
    }
    final_failure_rows = [
        json.loads(line)
        for line in (
            ROOT / "analysis/final_failure_classification_203.jsonl"
        )
        .read_text(encoding="utf-8")
        .splitlines()
        if line.strip()
    ]
    expected_final_failures = {
        (row["configuration"], row["task"], row["final_trial"])
        for row in final_outcomes
        if row["configuration"] in rq3_configurations
        and row["final_reward"] != "1.0"
    }
    observed_final_failures = {
        (row["configuration"], row["task"], row["trial"])
        for row in final_failure_rows
    }
    if (
        len(final_failure_rows) != len(expected_final_failures)
        or len(observed_final_failures) != len(expected_final_failures)
        or observed_final_failures != expected_final_failures
    ):
        raise SystemExit(
            "final failure classification does not cover all RQ3 non-passes"
        )
    failure_configurations = sorted(rq3_configurations)
    failure_categories = [
        "incomplete-migration",
        "wrong-root-cause",
        "wrong-semantic-output",
        "infra-exception",
        "gave-up-or-budget",
        "no-upgrade-attempted",
        "compile-namespace-inconsistency",
        "install-build-failure",
        "test-tampering",
    ]
    expected_failure_counts = {
        configuration: Counter(
            row["category"]
            for row in final_failure_rows
            if row["configuration"] == configuration
        )
        for configuration in failure_configurations
    }
    failure_count_rows = list(
        csv.DictReader(
            (
                ROOT / "analysis/final_failure_category_counts_203.csv"
            ).open(encoding="utf-8")
        )
    )
    if [row["category"] for row in failure_count_rows] != failure_categories:
        raise SystemExit("final failure category-count rows are stale")
    for row in failure_count_rows:
        category = row["category"]
        expected_total = 0
        for configuration in failure_configurations:
            expected = expected_failure_counts[configuration][category]
            if int(row[configuration]) != expected:
                raise SystemExit(
                    f"{configuration}/{category}: failure count is stale"
                )
            expected_total += expected
        if int(row["total"]) != expected_total:
            raise SystemExit(f"{category}: total failure count is stale")

    failure_summary = json.loads(
        (
            ROOT / "analysis/final_failure_summary_203.json"
        ).read_text(encoding="utf-8")
    )
    total_failure_counts = Counter(
        row["category"] for row in final_failure_rows
    )
    classification_sources = Counter(
        row["classification_source"] for row in final_failure_rows
    )
    if (
        failure_summary.get("cells") != len(final_failure_rows)
        or failure_summary.get("category_counts")
        != {
            category: total_failure_counts[category]
            for category in failure_categories
        }
        or failure_summary.get("classification_sources")
        != dict(sorted(classification_sources.items()))
    ):
        raise SystemExit("final failure summary totals are stale")
    expected_failure_configurations = {
        configuration: {
            "non_passes": sum(
                row["configuration"] == configuration
                for row in final_failure_rows
            ),
            "category_counts": {
                category: expected_failure_counts[configuration][category]
                for category in failure_categories
            },
        }
        for configuration in failure_configurations
    }
    if (
        failure_summary.get("configurations")
        != expected_failure_configurations
    ):
        raise SystemExit("final failure summary by configuration is stale")

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

    paper_numbers = json.loads(
        (ROOT / "analysis/paper_numbers_203.json").read_text(encoding="utf-8")
    )
    expected_pass_counts = {
        configuration: sum(
            row["final_reward"] == "1.0"
            for row in final_outcomes
            if row["configuration"] == configuration
        )
        for configuration in CONFIGURATIONS
    }
    if paper_numbers.get("pass_counts") != expected_pass_counts:
        raise SystemExit("paper pass counts are stale")
    runtime_summary = json.loads(
        (
            ROOT / "analysis/runtime_exception_rerun_summary_203.json"
        ).read_text(encoding="utf-8")
    )
    expected_non_pass_counts = {
        configuration: 203 - count
        for configuration, count in expected_pass_counts.items()
    }
    expected_ecosystem_pass_counts = {}
    ecosystems = sorted(set(task_ecosystems.values()))
    for configuration in sorted(CONFIGURATIONS):
        counts = Counter(
            task_ecosystems[row["task"]]
            for row in final_outcomes
            if row["configuration"] == configuration
            and row["final_reward"] == "1.0"
        )
        expected_ecosystem_pass_counts[configuration] = {
            ecosystem: counts[ecosystem] for ecosystem in ecosystems
        }

    pass_maps = {
        configuration: {
            row["task"]: row["final_reward"] == "1.0"
            for row in final_outcomes
            if row["configuration"] == configuration
        }
        for configuration in CONFIGURATIONS
    }
    expected_overlap = {}
    expected_overlap_totals = {}
    llms = sorted(
        {configuration.split("__", 1)[0] for configuration in CONFIGURATIONS}
    )
    for llm in llms:
        configurations = sorted(
            configuration
            for configuration in CONFIGURATIONS
            if configuration.startswith(f"{llm}__")
        )
        expected_overlap[llm] = {}
        totals = Counter()
        for ecosystem in ecosystems:
            tasks = [
                task
                for task, value in task_ecosystems.items()
                if value == ecosystem
            ]
            counts = Counter()
            for task in tasks:
                passes = sum(
                    pass_maps[configuration][task]
                    for configuration in configurations
                )
                if passes == 0:
                    counts["zero"] += 1
                elif passes == len(configurations):
                    counts["all"] += 1
                else:
                    counts["partial"] += 1
            expected_overlap[llm][ecosystem] = {
                key: counts[key]
                for key in ("zero", "partial", "all")
                if counts[key]
            }
            totals.update(counts)
        expected_overlap_totals[llm] = {
            "harnesses": len(configurations),
            "zero": totals["zero"],
            "partial": totals["partial"],
            "all": totals["all"],
        }

    if (
        paper_numbers.get("benchmark_tasks") != 203
        or paper_numbers.get("non_pass_counts") != expected_non_pass_counts
        or paper_numbers.get("ecosystem_pass_counts")
        != expected_ecosystem_pass_counts
        or paper_numbers.get("pass_overlap") != expected_overlap
        or paper_numbers.get("pass_overlap_totals")
        != expected_overlap_totals
    ):
        raise SystemExit("paper ecosystem or overlap numbers are stale")
    if (
        runtime_summary.get("benchmark_tasks") != 203
        or runtime_summary.get("pass_counts") != expected_pass_counts
        or runtime_summary.get("ecosystem_pass_counts")
        != expected_ecosystem_pass_counts
        or runtime_summary.get("pass_overlap") != expected_overlap
        or runtime_summary.get("gpt55_zero_pass_total")
        != expected_overlap_totals["gpt55"]["zero"]
        or runtime_summary.get("gpt55_all_pass_total")
        != expected_overlap_totals["gpt55"]["all"]
    ):
        raise SystemExit("runtime ecosystem or overlap numbers are stale")

    test_patch_rows = list(
        csv.DictReader(
            (
                ROOT / "analysis/test_patch_behavior_classification_203.csv"
            ).open(encoding="utf-8")
        )
    )
    if (
        len(test_patch_rows) != 203
        or {row["folder"] for row in test_patch_rows} != active_tasks
    ):
        raise SystemExit("test-patch behavior rows do not match the release")
    gpt_configurations = sorted(
        configuration
        for configuration in CONFIGURATIONS
        if configuration.startswith("gpt55__")
    )
    gpt_passes = {
        configuration: {
            row["task"]: row["final_reward"] == "1.0"
            for row in final_outcomes
            if row["configuration"] == configuration
        }
        for configuration in gpt_configurations
    }
    zero_pass = {
        task
        for task in active_tasks
        if not any(gpt_passes[configuration][task] for configuration in gpt_configurations)
    }
    all_pass = {
        task
        for task in active_tasks
        if all(gpt_passes[configuration][task] for configuration in gpt_configurations)
    }
    expected_quality = {}
    for category in (
        "ADDS_NEW_TESTS",
        "CORRECTS_EXISTING_BEHAVIOR",
        "MIXED",
        "TEST_INFRA_OR_FIXTURE_ONLY",
    ):
        category_tasks = {
            row["folder"]
            for row in test_patch_rows
            if row["primary_classification"] == category
        }
        expected_quality[category] = {
            "tasks": len(category_tasks),
            "zero_pass": len(category_tasks & zero_pass),
        }
    test_patch_by_task = {
        row["folder"]: row for row in test_patch_rows
    }

    def expected_surface(tasks: set[str]) -> dict[str, float | int]:
        changed_lines = [
            int(test_patch_by_task[task]["added_lines"])
            + int(test_patch_by_task[task]["deleted_lines"])
            for task in tasks
        ]
        files = [
            int(test_patch_by_task[task]["files_touched"]) for task in tasks
        ]
        return {
            "tasks": len(tasks),
            "mean_changed_lines": sum(changed_lines) / len(changed_lines),
            "mean_files_touched": sum(files) / len(files),
        }

    expected_hidden_test_patch = {
        "zero_pass": expected_surface(zero_pass),
        "all_pass": expected_surface(all_pass),
    }
    for document_name, document in (
        ("runtime summary", runtime_summary),
        ("paper numbers", paper_numbers),
    ):
        if (
            document.get("gpt55_test_quality_zero_pass")
            != expected_quality
            or document.get("gpt55_hidden_test_patch_stats")
            != expected_hidden_test_patch
            or document.get("trajectory_recovery_failure_analysis")
            != recovery_summary
            or document.get("environment_repair_rerun")
            != environment_summary
        ):
            raise SystemExit(
                f"{document_name} derived analysis numbers are stale"
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

    final_by_cell = {
        (row["configuration"], row["task"]): row for row in final_outcomes
    }
    final_trajectory_rows = {}
    for directory in ("trajectories", "verify_logs"):
        files = sorted((ROOT / directory).glob("*.jsonl.gz"))
        if len(files) != 10:
            raise SystemExit(f"expected 10 {directory} files, got {len(files)}")
        for path in files:
            stem = path.name.removesuffix(".jsonl.gz")
            with gzip.open(path, "rt", encoding="utf-8") as handle:
                rows = [json.loads(line) for line in handle]
            if len(rows) != 203:
                raise SystemExit(f"{path}: expected 203 rows, got {len(rows)}")
            if len({row["task"] for row in rows}) != 203:
                raise SystemExit(f"{path}: expected 203 unique tasks")
            if directory == "trajectories" and any(
                not row.get("trajectory") for row in rows
            ):
                raise SystemExit(f"{path}: expected 203 non-empty trajectories")
            for row in rows:
                outcome = final_by_cell[(stem, row["task"])]
                expected_reward = (
                    None
                    if outcome["final_reward"] == ""
                    else float(outcome["final_reward"])
                )
                if row.get("trial") != outcome["final_trial"]:
                    raise SystemExit(
                        f"{path}/{row['task']}: artifact trial does not match final outcome"
                    )
                if row.get("reward") != expected_reward:
                    raise SystemExit(
                        f"{path}/{row['task']}: artifact reward does not match final outcome"
                    )
                if row.get("outcome_source", "") != outcome["outcome_source"]:
                    raise SystemExit(
                        f"{path}/{row['task']}: artifact outcome source does not "
                        "match final outcome"
                    )
                if row.get("source_job", "") != outcome["final_job"]:
                    raise SystemExit(
                        f"{path}/{row['task']}: artifact source job does not "
                        "match final outcome"
                    )
                if directory == "trajectories":
                    key = (stem, row["task"], row["trial"])
                    if key in final_trajectory_rows:
                        raise SystemExit(f"{path}: duplicate final trajectory key {key}")
                    final_trajectory_rows[key] = {
                        "outcome_source": row.get("outcome_source", ""),
                        "passed": row.get("reward") == 1.0,
                    }

    per_trial_rows = count_gzip_jsonl(ROOT / "results/per_trial_results.jsonl.gz")
    if per_trial_rows != 2030:
        raise SystemExit(f"expected 2030 per-trial rows, got {per_trial_rows}")
    original_per_trial_rows = count_gzip_jsonl(
        ROOT / "results/original_per_trial_results.jsonl.gz"
    )
    if original_per_trial_rows != 2030:
        raise SystemExit(
            f"expected 2030 original per-trial rows, got {original_per_trial_rows}"
        )

    bundle_manifest_value = manifest.get("environment_repair_job_bundle")
    if not bundle_manifest_value:
        raise SystemExit("MANIFEST does not identify the environment job bundle")
    bundle_manifest_path = ROOT / bundle_manifest_value
    if not bundle_manifest_path.is_file():
        raise SystemExit("environment job-bundle manifest is missing")
    bundle = json.loads(bundle_manifest_path.read_text(encoding="utf-8"))
    if (
        bundle.get("tasks") != 24
        or bundle.get("configurations") != 10
        or bundle.get("trials") != 240
        or int(bundle.get("raw_trials", 0)) < 240
        or bundle.get("replacement_trials")
        != int(bundle.get("raw_trials", 0)) - 240
        or len(bundle.get("archives", [])) != 11
    ):
        raise SystemExit("environment job-bundle manifest is stale")
    bundle_root = bundle_manifest_path.parent
    archive_rows = bundle["archives"]
    archive_configurations = [
        row["configuration"] for row in archive_rows
    ]
    expected_archive_configurations = [
        *sorted(JOB_CONFIGURATIONS),
        "run_metadata",
    ]
    if sorted(archive_configurations) != sorted(
        expected_archive_configurations
    ):
        raise SystemExit(
            "environment job bundle must contain exactly one archive for "
            "each raw Harbor configuration and one run_metadata archive"
        )
    listed_archives = set()
    archived_raw_trials = 0
    archived_result_paths = set()
    metadata_all_trial_paths = None
    metadata_final_trial_paths = None
    for row in bundle["archives"]:
        relative = Path(row["file"])
        if relative.is_absolute() or ".." in relative.parts:
            raise SystemExit(f"unsafe job-bundle path: {relative}")
        path = (bundle_root / relative).resolve()
        try:
            path.relative_to(bundle_root.resolve())
        except ValueError as error:
            raise SystemExit(
                f"job-bundle archive escapes its root: {path}"
            ) from error
        if path in listed_archives:
            raise SystemExit(f"duplicate job-bundle archive path: {path}")
        listed_archives.add(path)
        if (
            not path.is_file()
            or path.stat().st_size != int(row["bytes"])
            or sha256(path) != row["sha256"]
        ):
            raise SystemExit(f"job-bundle archive is invalid: {path}")
        expected_selected_trials = (
            240 if row["configuration"] == "run_metadata" else 24
        )
        if int(row.get("selected_trials", -1)) != expected_selected_trials:
            raise SystemExit(
                f"job-bundle selected-trial count is stale: {path}"
            )
        if int(row["trials"]) < expected_selected_trials:
            raise SystemExit(f"job-bundle raw-trial count is stale: {path}")
        if row["configuration"] == "run_metadata":
            if int(row["trials"]) != int(bundle["raw_trials"]):
                raise SystemExit(
                    "job metadata archive raw-trial count is stale"
                )
        else:
            archived_raw_trials += int(row["trials"])
        try:
            with tarfile.open(path, "r:gz") as archive:
                members = archive.getmembers()
                member_names = [member.name for member in members]
                if len(member_names) != len(set(member_names)):
                    raise SystemExit(
                        f"job-bundle archive has duplicate members: {path}"
                    )
                for member in members:
                    member_path = PurePosixPath(member.name)
                    if (
                        member_path.is_absolute()
                        or ".." in member_path.parts
                        or not member.isfile()
                    ):
                        raise SystemExit(
                            f"unsafe job-bundle member in {path}: "
                            f"{member.name}"
                        )
                configuration = row["configuration"]
                if configuration == "run_metadata":
                    required_metadata = {
                        "manifests/affected_tasks_24.txt",
                        "manifests/infra_retry_cells.json",
                        "analysis/all_trials.csv",
                        "analysis/final_trials.csv",
                        "analysis/final_summary.json",
                    }
                    if not required_metadata.issubset(member_names):
                        raise SystemExit(
                            f"job metadata archive is incomplete: {path}"
                        )
                    extracted = archive.extractfile(
                        "analysis/all_trials.csv"
                    )
                    if extracted is None:
                        raise SystemExit(
                            "cannot read archived analysis/all_trials.csv"
                        )
                    metadata_rows = list(
                        csv.DictReader(
                            io.StringIO(
                                extracted.read().decode("utf-8")
                            )
                        )
                    )
                    metadata_all_trial_paths = {
                        row["path"] for row in metadata_rows
                    }
                    if (
                        len(metadata_rows) != int(bundle["raw_trials"])
                        or len(metadata_all_trial_paths)
                        != len(metadata_rows)
                    ):
                        raise SystemExit(
                            "archived all_trials.csv does not describe "
                            "the raw job bundle"
                        )
                    final_extracted = archive.extractfile(
                        "analysis/final_trials.csv"
                    )
                    if final_extracted is None:
                        raise SystemExit(
                            "cannot read archived analysis/final_trials.csv"
                        )
                    metadata_final_rows = list(
                        csv.DictReader(
                            io.StringIO(
                                final_extracted.read().decode("utf-8")
                            )
                        )
                    )
                    metadata_final_trial_paths = {
                        str(PurePosixPath(row["path"]).parent)
                        for row in metadata_final_rows
                    }
                    expected_final_trial_paths = {
                        row["trial_dir"] for row in environment_rows
                    }
                    if (
                        len(metadata_final_rows) != 240
                        or len(metadata_final_trial_paths) != 240
                        or metadata_final_trial_paths
                        != expected_final_trial_paths
                    ):
                        raise SystemExit(
                            "archived final_trials.csv does not match "
                            "release provenance"
                        )
                    retry_extracted = archive.extractfile(
                        "manifests/infra_retry_cells.json"
                    )
                    if retry_extracted is None:
                        raise SystemExit(
                            "cannot read archived infrastructure retry manifest"
                        )
                    retry_manifest = json.loads(retry_extracted.read())
                    replaced_results = {
                        row["replaced_result"]
                        for row in retry_manifest["cells"]
                    }
                    if not replaced_results <= metadata_all_trial_paths:
                        raise SystemExit(
                            "archived raw inventory dropped a replaced "
                            "setup-timeout result"
                        )
                    continue

                result_members = [
                    member
                    for member in members
                    if (
                        len(PurePosixPath(member.name).parts) == 5
                        and PurePosixPath(member.name).name == "result.json"
                        and PurePosixPath(member.name).parts[0]
                        in {
                            "harbor_jobs",
                            "harbor_jobs_path_fix",
                            "harbor_jobs_path_fix_retries",
                        }
                        and PurePosixPath(member.name).parts[1]
                        == configuration
                    )
                ]
                if len(result_members) != int(row["trials"]):
                    raise SystemExit(
                        f"{configuration}: archived raw-trial count is stale"
                    )
                final_configuration = JOB_CONFIGURATIONS[configuration]
                expected_by_task = {
                    item["task"]: item
                    for item in environment_rows
                    if item["configuration"] == final_configuration
                }
                observed_tasks = set()
                selected_tasks = set()
                names = set(member_names)
                for member in result_members:
                    archived_result_paths.add(member.name)
                    extracted = archive.extractfile(member)
                    if extracted is None:
                        raise SystemExit(
                            f"cannot read archived result: {member.name}"
                        )
                    result = json.loads(extracted.read())
                    task = str(
                        result.get("task_name") or ""
                    ).split("/")[-1]
                    if task not in expected_by_task:
                        raise SystemExit(
                            f"{configuration}: unexpected "
                            f"archived task {task!r}"
                        )
                    observed_tasks.add(task)
                    trial_root = PurePosixPath(member.name).parent
                    parts = trial_root.parts
                    if (
                        len(parts) != 4
                        or parts[0]
                        not in {
                            "harbor_jobs",
                            "harbor_jobs_path_fix",
                            "harbor_jobs_path_fix_retries",
                        }
                        or parts[1] != configuration
                    ):
                        raise SystemExit(
                            f"{configuration}: unexpected trial path "
                            f"{trial_root}"
                        )
                    expected = expected_by_task[task]
                    if str(trial_root) == expected["trial_dir"]:
                        if task in selected_tasks:
                            raise SystemExit(
                                f"{configuration}/{task}: selected trial "
                                "is archived more than once"
                            )
                        selected_tasks.add(task)
                        if result_reward(result) != float(
                            expected["reward"] or 0
                        ):
                            raise SystemExit(
                                f"{configuration}/{task}: archived reward "
                                "does not match release provenance"
                            )
                    required_raw_trial_members = {
                        str(trial_root / "config.json"),
                        str(trial_root / "result.json"),
                        str(trial_root / "trial.log"),
                    }
                    if not required_raw_trial_members.issubset(names):
                        raise SystemExit(
                            f"{configuration}/{task}: archived trial is "
                            "missing required files"
                        )
                    if str(trial_root) != expected["trial_dir"]:
                        continue
                    if str(trial_root / "verifier/reward.txt") not in names:
                        raise SystemExit(
                            f"{configuration}/{task}: selected trial is "
                            "missing its verifier reward"
                        )
                    if not any(
                        str(trial_root / candidate) in names
                        for candidate in (
                            "verifier/test-stdout.txt",
                            "verifier/ctrf.json",
                        )
                    ):
                        raise SystemExit(
                            f"{configuration}/{task}: archived verifier "
                            "evidence is missing"
                        )
                    agent_prefix = str(trial_root / "agent") + "/"
                    if not any(
                        name.startswith(agent_prefix) for name in names
                    ):
                        raise SystemExit(
                            f"{configuration}/{task}: archived agent log "
                            "is missing"
                        )
                if (
                    observed_tasks != ENVIRONMENT_REPAIR_TASKS
                    or selected_tasks != ENVIRONMENT_REPAIR_TASKS
                ):
                    raise SystemExit(
                        f"{configuration}: archived task selection is stale"
                    )
        except (tarfile.TarError, OSError, json.JSONDecodeError) as error:
            raise SystemExit(
                f"cannot inspect job-bundle archive {path}: {error}"
            ) from error
    if archived_raw_trials != int(bundle["raw_trials"]):
        raise SystemExit(
            "job-bundle raw-trial total does not match configuration archives"
        )
    if (
        metadata_all_trial_paths is None
        or metadata_final_trial_paths is None
        or archived_result_paths != metadata_all_trial_paths
    ):
        raise SystemExit(
            "archived result paths do not exactly match all_trials.csv"
        )
    actual_archives = set(
        (bundle_root / "archives").glob("*.tar.gz")
    )
    if actual_archives != listed_archives:
        raise SystemExit(
            "job-bundle archives differ from the manifest: "
            f"extra={sorted(actual_archives - listed_archives)} "
            f"missing={sorted(listed_archives - actual_archives)}"
        )

    required = [
        "README.md",
        "LICENSE.txt",
        "NOTICE.txt",
        "CONTRIBUTING.md",
        "SECURITY.md",
        "CODE_OF_CONDUCT.md",
        "SUPPORT.md",
        "THIRD_PARTY_NOTICES.md",
        "OPEN_SOURCE_RELEASE_CHECKLIST.md",
        "MANIFEST.json",
        "pyproject.toml",
        "setup.cfg",
        "setup.py",
        "analysis/ecosystem_results.csv",
        "analysis/coverage.csv",
        "analysis/repository_metadata.csv",
        "analysis/repository_metadata.json",
        "analysis/task_repository_metadata.csv",
        "analysis/runtime_exception_rerun_summary_203.json",
        "analysis/original_full_run_trajectory_scan_summary.csv",
        "analysis/paper_numbers_203.json",
        "analysis/trajectory_behavior_annotations_203.jsonl",
        "analysis/trajectory_behavior_annotation_protocol.md",
        "analysis/trajectory_behavior_summary_203.csv",
        "analysis/trajectory_behavior_by_source_203.csv",
        "analysis/trajectory_behavior_summary_203.json",
        "analysis/trajectory_recovery_failure_classification_203.jsonl",
        "analysis/trajectory_recovery_failure_category_counts_203.csv",
        "analysis/trajectory_recovery_failure_summary_203.json",
        "analysis/final_failure_classification_203.jsonl",
        "analysis/final_failure_category_counts_203.csv",
        "analysis/final_failure_summary_203.json",
        "analysis/environment_repair_rerun_summary_203.json",
        "analysis/test_contract_repair_decisions_2026-07-14.md",
        "analysis/test_contract_repair_decisions_2026-07-14.csv",
        "analysis/test_patch_behavior_classification_203.csv",
        "analysis/release_redactions_2026-07-23.csv",
        "analysis/secret_scan_review_2026-07-23.csv",
        "assets/benchmark-flow.svg",
        "assets/benchmark-flow-dark.svg",
        "assets/benchmark-flow-mobile.svg",
        "assets/benchmark-flow-mobile-dark.svg",
        "results/final_per_task_outcomes.csv",
        "results/original_per_trial_results.jsonl.gz",
        "results/targeted_runtime_exception_reruns_203.csv",
        "results/trajectory_recovery_reruns_203.csv",
        "results/task_metadata_correction_reruns_203.csv",
        "results/affected_contract_reruns_203.csv",
        "results/environment_repair_reruns_203.csv",
        "repro/download_benchmark.py",
        "repro/audit_release_compliance.py",
        "repro/collect_repository_metadata.py",
        "repro/package_harbor_jobs.py",
        "repro/repair_task_image_toolchain_paths.py",
        "repro/sync_targeted_rerun_results.py",
        "repro/rebuild_final_artifacts.py",
        "repro/rebuild_final_failure_classification.py",
        "repro/sync_affected_contract_reruns.py",
        "repro/sync_affected_trajectory_behavior_annotations.py",
        "repro/sync_environment_repair_reruns.py",
        "repro/sync_environment_trajectory_behavior_annotations.py",
        "repro/recompute_analysis.py",
        "repro/build_failure_annotation_packets.py",
        "repro/summarize_recovery_failure_annotations.py",
        "repro/redact_release_trajectories.py",
        "repro/refresh_secret_scan_review.py",
        "repro/trajectory_conversion.py",
        "repro/TASK_SCHEMA.md",
        "repro/run_oracle_solution.sh",
        "repro/run_patch_verifier.sh",
        "repro/scan_trajectories.py",
        "repro/summarize_trajectory_behavior_annotations.py",
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
        if config["agents"][0]["env"]:
            raise SystemExit(f"{path}: checked-in agent env must be empty")
        if "opencode" in path.name and config["agents"][0]["kwargs"].get("version") != "1.17.11":
            raise SystemExit(f"{path}: expected pinned OpenCode version 1.17.11")

    for path in [
        "analysis/trajectory_scan_detail.csv",
        "analysis/trajectory_scan_summary.csv",
        "analysis/trajectory_scan_by_source.csv",
        "analysis/trajectory_scan_summary.json",
    ]:
        if not (ROOT / path).exists():
            raise SystemExit(f"missing trajectory scan output: {path}")

    behavior_rows = [
        json.loads(line)
        for line in (
            ROOT / "analysis/trajectory_behavior_annotations_203.jsonl"
        )
        .read_text(encoding="utf-8")
        .splitlines()
        if line.strip()
    ]
    behavior_by_key = {
        (row["configuration"], row["task"], row["trial"]): row
        for row in behavior_rows
    }
    if len(behavior_rows) != 2030 or len(behavior_by_key) != 2030:
        raise SystemExit(
            "expected 2,030 unique trajectory behavior annotations"
        )
    if set(behavior_by_key) != set(final_trajectory_rows):
        raise SystemExit(
            "trajectory behavior annotations do not match the final trajectory keys"
        )

    behaviors = (
        "docs_lookup",
        "api_source_inspection",
        "ran_tests",
        "bc_hypothesis",
    )
    for key, row in behavior_by_key.items():
        if any(type(row.get(behavior)) is not bool for behavior in behaviors):
            raise SystemExit(f"{key}: trajectory behavior labels must be boolean")
        if any(
            not isinstance(row.get(field), str) or not row[field]
            for field in ("annotation_source", "annotator")
        ):
            raise SystemExit(f"{key}: missing trajectory annotation provenance")

    configuration_counts = Counter(
        row["configuration"] for row in behavior_rows
    )
    expected_configurations = {
        row["configuration"] for row in final_outcomes
    }
    if (
        set(configuration_counts) != expected_configurations
        or any(count != 203 for count in configuration_counts.values())
    ):
        raise SystemExit(
            "trajectory behavior annotations must cover 203 rows for each "
            "of the 10 final configurations"
        )

    def expected_behavior_summary(group_fields):
        grouped = {}
        for key, row in behavior_by_key.items():
            final = final_trajectory_rows[key]
            group_key = tuple(
                row[field]
                if field != "outcome_source"
                else final["outcome_source"]
                for field in group_fields
            )
            record = grouped.setdefault(
                group_key,
                {
                    "rows": 0,
                    "passes": 0,
                    "non_passes": 0,
                    **{behavior: 0 for behavior in behaviors},
                },
            )
            record["rows"] += 1
            record["passes"] += final["passed"]
            record["non_passes"] += not final["passed"]
            for behavior in behaviors:
                record[behavior] += row[behavior]
        return grouped

    for path, group_fields in (
        (
            ROOT / "analysis/trajectory_behavior_summary_203.csv",
            ("configuration",),
        ),
        (
            ROOT / "analysis/trajectory_behavior_by_source_203.csv",
            ("configuration", "outcome_source"),
        ),
    ):
        observed_rows = list(csv.DictReader(path.open()))
        observed = {
            tuple(row[field] for field in group_fields): {
                field: int(row[field])
                for field in ("rows", "passes", "non_passes", *behaviors)
            }
            for row in observed_rows
        }
        expected = expected_behavior_summary(group_fields)
        if len(observed_rows) != len(observed) or observed != expected:
            raise SystemExit(f"{path}: trajectory behavior summary is stale")

    def expected_behavior_rows(group_fields):
        grouped = expected_behavior_summary(group_fields)
        return [
            {
                **dict(zip(group_fields, key)),
                **values,
            }
            for key, values in sorted(grouped.items())
        ]

    behavior_payload = json.loads(
        (
            ROOT / "analysis/trajectory_behavior_summary_203.json"
        ).read_text(encoding="utf-8")
    )
    expected_summary_rows = expected_behavior_rows(("configuration",))
    expected_source_rows = expected_behavior_rows(
        ("configuration", "outcome_source")
    )
    expected_annotation_sources = dict(
        sorted(
            Counter(
                row["annotation_source"] for row in behavior_rows
            ).items()
        )
    )
    expected_annotators = dict(
        sorted(Counter(row["annotator"] for row in behavior_rows).items())
    )
    if (
        behavior_payload.get("behaviors") != list(behaviors)
        or behavior_payload.get("summary") != expected_summary_rows
        or behavior_payload.get("summary_by_source") != expected_source_rows
        or behavior_payload.get("annotation_sources")
        != expected_annotation_sources
        or behavior_payload.get("annotators") != expected_annotators
    ):
        raise SystemExit("trajectory behavior JSON summary is stale")

    expected_final_scan = {
        row["configuration"]: {
            "rows": row["rows"],
            "with_trajectory": row["rows"],
            "docs_lookup": row["docs_lookup"],
            "dependency_api_lookup": row["api_source_inspection"],
            "test_or_build_feedback": row["ran_tests"],
            "breaking_change_reasoning": row["bc_hypothesis"],
        }
        for row in expected_summary_rows
    }
    expected_final_scan_by_source = {}
    for row in expected_source_rows:
        expected_final_scan_by_source.setdefault(
            row["configuration"], {}
        )[row["outcome_source"]] = {
            "rows": row["rows"],
            "passes": row["passes"],
            "non_passes": row["non_passes"],
            "with_trajectory": row["rows"],
            "docs_lookup": row["docs_lookup"],
            "dependency_api_lookup": row["api_source_inspection"],
            "test_or_build_feedback": row["ran_tests"],
            "breaking_change_reasoning": row["bc_hypothesis"],
        }
    for document_name, document in (
        ("runtime summary", runtime_summary),
        ("paper numbers", paper_numbers),
    ):
        if (
            document.get("final_trajectory_scan")
            != expected_final_scan
            or document.get("final_trajectory_scan_by_source")
            != expected_final_scan_by_source
        ):
            raise SystemExit(
                f"{document_name} trajectory summary is stale"
            )

    print("DepBench release validation passed: 203 tasks, 10 configurations, 2030 reported trials.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
