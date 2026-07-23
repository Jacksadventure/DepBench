#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

from __future__ import annotations

import argparse
import csv
import gzip
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

DOC_RE = re.compile(
    r"\b(web_search|websearch|web_fetch|webfetch|curl\s+[^\n]*https?://|"
    r"wget\s+[^\n]*https?://|https?://[^\s]*(docs|documentation|release|"
    r"changelog|migration|upgrade)|release notes?|changelog|migration guide|"
    r"upgrade guide|official docs?|documentation)\b",
    re.I,
)
API_RE = re.compile(
    r"\b(node_modules|vendor/|\.m2/repository|\.cargo/registry|go/pkg/mod|"
    r"grep|rg\s+|ripgrep|sed -n|javap|go doc|cargo doc|npm view|"
    r"dependency source|source code|signature|interface|method|class|function|"
    r"package\s+[A-Za-z0-9_.-]+)\b",
    re.I,
)
TEST_RE = re.compile(
    r"\b(pytest|npm test|yarn test|pnpm test|mvn test|gradle test|go test|"
    r"cargo test|cargo check|trybuild|jest|vitest|tsc|test suite|running tests?|"
    r"build failed|compile error|verifier|make test)\b",
    re.I,
)
CHANGE_RE = re.compile(
    r"\b(breaking change|migration|migrate|deprecated|removed|renamed|"
    r"incompatible|API change|signature changed|no longer|changed in|new API|"
    r"old API|upgrade requires)\b",
    re.I,
)


def stringify(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return "\n".join(stringify(item) for item in value)
    if isinstance(value, dict):
        pieces: list[str] = []
        for key in (
            "message",
            "reasoning_content",
            "content",
            "tool_calls",
            "observation",
            "arguments",
            "function_name",
            "results",
            "extra",
        ):
            if key in value:
                pieces.append(stringify(value[key]))
        return "\n".join(piece for piece in pieces if piece)
    return str(value)


def agent_text(trajectory: dict[str, Any] | None) -> str:
    if not trajectory:
        return ""
    chunks: list[str] = []
    for step in trajectory.get("steps", []):
        if step.get("source") == "agent":
            chunks.append(stringify(step))
    return "\n".join(chunks)


def scan_file(path: Path) -> list[dict[str, Any]]:
    configuration = path.name.removesuffix(".jsonl.gz")
    llm, harness = configuration.split("__", 1)
    rows: list[dict[str, Any]] = []
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        for line in handle:
            item = json.loads(line)
            text = agent_text(item.get("trajectory"))
            rows.append(
                {
                    "configuration": configuration,
                    "llm": llm,
                    "harness": harness,
                    "task": item.get("task"),
                    "trial": item.get("trial"),
                    "reward": item.get("reward"),
                    "outcome_source": item.get("outcome_source", ""),
                    "trajectory_source": item.get("trajectory_source", ""),
                    "exception_type": item.get("exception_type", ""),
                    "has_trajectory": bool(item.get("trajectory")),
                    "docs_lookup": bool(DOC_RE.search(text)),
                    "dependency_api_lookup": bool(API_RE.search(text)),
                    "test_or_build_feedback": bool(TEST_RE.search(text)),
                    "breaking_change_reasoning": bool(CHANGE_RE.search(text)),
                    "agent_text_chars": len(text),
                }
            )
    return rows


def scan_all(trajectory_dir: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted(trajectory_dir.glob("*.jsonl.gz")):
        rows.extend(scan_file(path))
    return rows


def summarize(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: list[dict[str, Any]] = []
    configurations = sorted({row["configuration"] for row in rows})
    for configuration in configurations:
        subset = [row for row in rows if row["configuration"] == configuration]
        first = subset[0]
        groups.append(
            {
                "configuration": configuration,
                "llm": first["llm"],
                "harness": first["harness"],
                "rows": len(subset),
                "with_trajectory": sum(row["has_trajectory"] for row in subset),
                "docs_lookup": sum(row["docs_lookup"] for row in subset),
                "dependency_api_lookup": sum(row["dependency_api_lookup"] for row in subset),
                "test_or_build_feedback": sum(row["test_or_build_feedback"] for row in subset),
                "breaking_change_reasoning": sum(row["breaking_change_reasoning"] for row in subset),
            }
        )
    return groups


def summarize_by_source(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: list[dict[str, Any]] = []
    keys = sorted(
        {
            (row["configuration"], row["outcome_source"])
            for row in rows
        }
    )
    for configuration, outcome_source in keys:
        subset = [
            row
            for row in rows
            if row["configuration"] == configuration
            and row["outcome_source"] == outcome_source
        ]
        first = subset[0]
        groups.append(
            {
                "configuration": configuration,
                "llm": first["llm"],
                "harness": first["harness"],
                "outcome_source": outcome_source,
                "rows": len(subset),
                "passes": sum(float(row["reward"] or 0) == 1.0 for row in subset),
                "non_passes": sum(float(row["reward"] or 0) != 1.0 for row in subset),
                "with_trajectory": sum(row["has_trajectory"] for row in subset),
                "docs_lookup": sum(row["docs_lookup"] for row in subset),
                "dependency_api_lookup": sum(
                    row["dependency_api_lookup"] for row in subset
                ),
                "test_or_build_feedback": sum(
                    row["test_or_build_feedback"] for row in subset
                ),
                "breaking_change_reasoning": sum(
                    row["breaking_change_reasoning"] for row in subset
                ),
            }
        )
    return groups


def write_outputs(rows: list[dict[str, Any]], out_dir: Path, prefix: str) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    detail_path = out_dir / f"{prefix}_detail.csv"
    summary_path = out_dir / f"{prefix}_summary.csv"
    by_source_path = out_dir / f"{prefix}_by_source.csv"
    json_path = out_dir / f"{prefix}_summary.json"

    detail_cols = [
        "configuration",
        "llm",
        "harness",
        "task",
        "trial",
        "reward",
        "outcome_source",
        "trajectory_source",
        "exception_type",
        "has_trajectory",
        "docs_lookup",
        "dependency_api_lookup",
        "test_or_build_feedback",
        "breaking_change_reasoning",
        "agent_text_chars",
    ]
    with detail_path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=detail_cols, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    summary_rows = summarize(rows)
    summary_cols = [
        "configuration",
        "llm",
        "harness",
        "rows",
        "with_trajectory",
        "docs_lookup",
        "dependency_api_lookup",
        "test_or_build_feedback",
        "breaking_change_reasoning",
    ]
    with summary_path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=summary_cols, lineterminator="\n")
        writer.writeheader()
        writer.writerows(summary_rows)

    by_source_rows = summarize_by_source(rows)
    by_source_cols = [
        "configuration",
        "llm",
        "harness",
        "outcome_source",
        "rows",
        "passes",
        "non_passes",
        "with_trajectory",
        "docs_lookup",
        "dependency_api_lookup",
        "test_or_build_feedback",
        "breaking_change_reasoning",
    ]
    with by_source_path.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=by_source_cols, lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(by_source_rows)

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "method": "Single rule-based scanner over agent-authored trajectory steps; prompt and system text are excluded.",
        "summary": summary_rows,
        "summary_by_source": by_source_rows,
    }
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--trajectory-dir", type=Path, default=ROOT / "trajectories")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "analysis")
    parser.add_argument("--prefix", default="trajectory_scan")
    args = parser.parse_args()

    rows = scan_all(args.trajectory_dir)
    write_outputs(rows, args.out_dir, args.prefix)
    print(f"scanned {len(rows)} rows from {args.trajectory_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
