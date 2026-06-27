#!/usr/bin/env python3
"""Scan discovery behaviors from exported LLM x harness trajectories.

Input is the gzip JSONL export produced by
``scripts/export_llm_harness_trajectories.py``.  The scanner deliberately uses
one rule set for every LLM/harness pair and excludes user/system prompt text,
so task instructions and PR URLs are not counted as agent discovery behavior.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_EXPORT_DIR = (
    Path(__file__).resolve().parents[1]
    / "harbor_benchmark/trajectory_exports/v4_withtest219_20260627"
)
DEFAULT_OUT_DIR = (
    Path(__file__).resolve().parents[1] / "harbor_benchmark/reports"
)

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
BC_RE = re.compile(
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


def scan_text(trajectory: dict[str, Any] | None) -> str:
    if not trajectory:
        return ""
    chunks: list[str] = []
    for step in trajectory.get("steps", []):
        if step.get("source") == "agent":
            chunks.append(stringify(step))
    return "\n".join(chunks)


def scan_exports(export_dir: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted(export_dir.glob("*.jsonl.gz")):
        group = path.name.removesuffix(".jsonl.gz")
        llm, harness = group.split("__", 1)
        with gzip.open(path, "rt", encoding="utf-8") as handle:
            for line in handle:
                item = json.loads(line)
                text = scan_text(item.get("trajectory"))
                rows.append(
                    {
                        "llm": llm,
                        "harness": harness,
                        "task": item.get("task"),
                        "trial": item.get("trial"),
                        "reward": item.get("reward"),
                        "has_trajectory": bool(item.get("trajectory")),
                        "docs": bool(DOC_RE.search(text)),
                        "api": bool(API_RE.search(text)),
                        "tests": bool(TEST_RE.search(text)),
                        "bc_hyp": bool(BC_RE.search(text)),
                        "chars": len(text),
                    }
                )
    return rows


def write_outputs(rows: list[dict[str, Any]], out_dir: Path, stamp: str) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    csv_path = out_dir / f"v4_withtest219_trajectory_behavior_unified_{stamp}.csv"
    json_path = out_dir / f"v4_withtest219_trajectory_behavior_unified_{stamp}.json"
    md_path = out_dir / f"v4_withtest219_trajectory_behavior_unified_{stamp}.md"

    fieldnames = [
        "llm",
        "harness",
        "task",
        "trial",
        "reward",
        "has_trajectory",
        "docs",
        "api",
        "tests",
        "bc_hyp",
        "chars",
    ]
    with csv_path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    groups: list[dict[str, Any]] = []
    for llm in sorted({row["llm"] for row in rows}):
        for harness in sorted({row["harness"] for row in rows if row["llm"] == llm}):
            subset = [row for row in rows if row["llm"] == llm and row["harness"] == harness]
            groups.append(
                {
                    "llm": llm,
                    "harness": harness,
                    "rows": len(subset),
                    "with_trajectory": sum(row["has_trajectory"] for row in subset),
                    "docs": sum(row["docs"] for row in subset),
                    "api": sum(row["api"] for row in subset),
                    "tests": sum(row["tests"] for row in subset),
                    "bc_hyp": sum(row["bc_hyp"] for row in subset),
                }
            )
    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "method": "Single scanner over exported trajectories; user/system prompt text is excluded.",
        "groups": groups,
    }
    json_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")

    lines = [
        "# Unified trajectory behavior scan",
        "",
        f"Generated: {summary['generated_at']}",
        "",
        "The scanner uses one rule set for every LLM--harness pair and excludes user/system prompt text.",
        "",
        "| LLM | Harness | Rows | With trajectory | Docs | API | Tests | BC hyp. |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for group in groups:
        lines.append(
            f"| {group['llm']} | {group['harness']} | {group['rows']} | "
            f"{group['with_trajectory']} | {group['docs']} | {group['api']} | "
            f"{group['tests']} | {group['bc_hyp']} |"
        )
    md_path.write_text("\n".join(lines) + "\n")
    print(json.dumps(summary, indent=2, sort_keys=True))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--export-dir", type=Path, default=DEFAULT_EXPORT_DIR)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--stamp", default="20260627")
    args = parser.parse_args()
    rows = scan_exports(args.export_dir)
    write_outputs(rows, args.out_dir, args.stamp)


if __name__ == "__main__":
    main()
