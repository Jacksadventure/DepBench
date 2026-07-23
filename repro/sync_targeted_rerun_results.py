#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""Merge final rerun outcomes into the released numeric result tables."""

from __future__ import annotations

import csv
import gzip
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RERUN_PATH = ROOT / "results/targeted_runtime_exception_reruns_203.csv"
RECOVERY_PATH = ROOT / "results/trajectory_recovery_reruns_203.csv"
FINAL_OUTCOMES_PATH = ROOT / "results/final_per_task_outcomes.csv"

RERUN_CONFIGURATIONS = {
    "codex_gpt55": ("codex", "gpt55"),
    "copilot_gemini": ("copilot_cli", "gemini35flash"),
    "copilot_gpt55": ("copilot_cli", "gpt55"),
    "opencode_gpt55": ("opencode", "gpt55"),
}


def rate(numerator: int, denominator: int) -> str:
    if denominator == 0:
        return "0"
    return f"{numerator / denominator:.6f}".rstrip("0").rstrip(".")


def clean_message(value: object) -> str:
    return "\n".join(
        line.rstrip() for line in str(value or "").splitlines()
    ).strip()


def read_baseline() -> list[dict]:
    path = ROOT / "results/original_per_trial_results.jsonl.gz"
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle]


def read_reruns() -> dict[tuple[str, str], dict]:
    rows = list(csv.DictReader(RERUN_PATH.open(encoding="utf-8")))
    reruns: dict[tuple[str, str], dict] = {}
    for row in rows:
        harness, llm = RERUN_CONFIGURATIONS[row["configuration"]]
        key = (f"{llm}__{harness}", row["task"])
        if key in reruns:
            raise SystemExit(f"duplicate rerun cell: {key}")
        reruns[key] = row | {
            "outcome_source": "targeted_rerun",
            "normalized_configuration": key[0],
        }

    if RECOVERY_PATH.exists():
        for row in csv.DictReader(RECOVERY_PATH.open(encoding="utf-8")):
            key = (row["configuration"], row["task"])
            if key in reruns:
                raise SystemExit(f"duplicate rerun cell: {key}")
            reruns[key] = row | {
                "outcome_source": "trajectory_recovery_rerun",
                "normalized_configuration": key[0],
            }
    return reruns


def build_final_outcomes(
    baseline: list[dict], reruns: dict[tuple[str, str], dict]
) -> list[dict]:
    outcomes = []
    matched_reruns = set()
    for row in baseline:
        configuration = f"{row['llm']}__{row['harness']}"
        key = (configuration, row["task"])
        rerun = reruns.get(key)
        original_reward = row.get("reward")
        if rerun:
            if (
                rerun["outcome_source"] == "targeted_rerun"
                and original_reward == 1.0
            ):
                raise SystemExit(f"rerun unexpectedly replaces a pass: {key}")
            final_reward = float(rerun["reward"])
            matched_reruns.add(key)
        else:
            final_reward = original_reward

        outcomes.append(
            {
                "configuration": configuration,
                "harness": row["harness"],
                "llm": row["llm"],
                "model": row["model"],
                "task": row["task"],
                "original_reward": "" if original_reward is None else original_reward,
                "final_reward": "" if final_reward is None else final_reward,
                "outcome_source": (
                    rerun["outcome_source"] if rerun else "original_full_run"
                ),
                "original_trial": row["trial"],
                "final_trial": rerun["trial"] if rerun else row["trial"],
                "final_job": rerun["job_name"] if rerun else "",
                "final_exception_type": (
                    rerun["exception_type"]
                    if rerun
                    else row.get("exception_type", "")
                ),
                "final_exception_message": (
                    clean_message(rerun["exception_message"])
                    if rerun
                    else clean_message(row.get("exception_message", ""))
                ),
                "rerun_trial": rerun["trial"] if rerun else "",
                "rerun_exception_type": rerun["exception_type"] if rerun else "",
                "rerun_exception_message": (
                    clean_message(rerun["exception_message"]) if rerun else ""
                ),
            }
        )

    missing = set(reruns) - matched_reruns
    if missing:
        raise SystemExit(f"rerun cells missing from release baseline: {sorted(missing)}")
    return outcomes


def write_final_outcomes(outcomes: list[dict]) -> None:
    fields = [
        "configuration",
        "harness",
        "llm",
        "model",
        "task",
        "original_reward",
        "final_reward",
        "outcome_source",
        "original_trial",
        "final_trial",
        "final_job",
        "final_exception_type",
        "final_exception_message",
        "rerun_trial",
        "rerun_exception_type",
        "rerun_exception_message",
    ]
    with FINAL_OUTCOMES_PATH.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(outcomes)


def outcome_counts(rows: list[dict]) -> Counter:
    counts = Counter()
    for row in rows:
        reward = row["final_reward"]
        if reward == 1.0:
            counts["pass"] += 1
        elif reward == "":
            counts["no_reward"] += 1
        else:
            counts["fail"] += 1
    return counts


def update_summary(outcomes: list[dict], rerun_counts: Counter) -> None:
    by_configuration: dict[str, list[dict]] = {}
    for row in outcomes:
        by_configuration.setdefault(row["configuration"], []).append(row)

    csv_path = ROOT / "results/summary.csv"
    summary_rows = list(csv.DictReader(csv_path.open(encoding="utf-8")))
    for row in summary_rows:
        configuration = f"{row['llm']}__{row['harness']}"
        counts = outcome_counts(by_configuration[configuration])
        tasks = len(by_configuration[configuration])
        reward_bearing = tasks - counts["no_reward"]
        row.update(
            {
                "tasks": str(tasks),
                "pass": str(counts["pass"]),
                "fail": str(counts["fail"]),
                "no_reward": str(counts["no_reward"]),
                "pass_rate_total": rate(counts["pass"], tasks),
                "pass_rate_reward_bearing": rate(
                    counts["pass"], reward_bearing
                ),
            }
        )

    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=summary_rows[0].keys(), lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(summary_rows)

    json_path = ROOT / "results/summary.json"
    document = json.loads(json_path.read_text(encoding="utf-8"))
    rows_by_name = {row["configuration"]: row for row in summary_rows}
    for row in document["configurations"]:
        csv_row = rows_by_name[row["configuration"]]
        for field in ("tasks", "pass", "fail", "no_reward"):
            row[field] = int(csv_row[field])
        for field in ("pass_rate_total", "pass_rate_reward_bearing"):
            row[field] = float(csv_row[field])
    document["generated_at"] = datetime.now(timezone.utc).isoformat()
    document["targeted_rerun_cells"] = rerun_counts["targeted_rerun"]
    document["trajectory_recovery_rerun_cells"] = rerun_counts[
        "trajectory_recovery_rerun"
    ]
    document["targeted_rerun_results"] = str(RERUN_PATH.relative_to(ROOT))
    if RECOVERY_PATH.exists():
        document["trajectory_recovery_rerun_results"] = str(
            RECOVERY_PATH.relative_to(ROOT)
        )
    json_path.write_text(
        json.dumps(document, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )


def update_ecosystem_results(outcomes: list[dict]) -> None:
    task_summary = json.loads(
        (ROOT / "dataset/task_summary.json").read_text(encoding="utf-8")
    )
    ecosystems = {row["folder"]: row["ecosystem"] for row in task_summary}
    grouped: dict[tuple[str, str], list[dict]] = {}
    for row in outcomes:
        key = (row["configuration"], ecosystems[row["task"]])
        grouped.setdefault(key, []).append(row)

    path = ROOT / "analysis/ecosystem_results.csv"
    rows = list(csv.DictReader(path.open(encoding="utf-8")))
    for row in rows:
        llm = (
            row["model"]
            .replace("gpt-5.5", "gpt55")
            .replace("gemini-3.5-flash", "gemini35flash")
            .replace("claude-opus-4-8", "claude48")
        )
        configuration = f"{llm}__{row['harness']}"
        subset = grouped[(configuration, row["ecosystem"])]
        counts = outcome_counts(subset)
        tasks = len(subset)
        reward_bearing = tasks - counts["no_reward"]
        row.update(
            {
                "tasks": str(tasks),
                "pass": str(counts["pass"]),
                "fail": str(counts["fail"]),
                "no_reward": str(counts["no_reward"]),
                "pass_rate_total": rate(counts["pass"], tasks),
                "pass_rate_reward_bearing": rate(
                    counts["pass"], reward_bearing
                ),
            }
        )

    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=rows[0].keys(), lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    baseline = read_baseline()
    reruns = read_reruns()
    outcomes = build_final_outcomes(baseline, reruns)
    if len(baseline) != 2030 or len(reruns) not in (111, 288):
        raise SystemExit(
            f"unexpected input sizes: baseline={len(baseline)} reruns={len(reruns)}"
        )
    write_final_outcomes(outcomes)
    update_summary(
        outcomes,
        Counter(row["outcome_source"] for row in reruns.values()),
    )
    update_ecosystem_results(outcomes)
    print(f"updated 2030 outcomes with {len(reruns)} final rerun cells")


if __name__ == "__main__":
    main()
