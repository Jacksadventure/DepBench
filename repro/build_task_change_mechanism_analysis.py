#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""Build the reviewed direct/indirect change-mechanism analysis for 203 tasks."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TASK_SUMMARY = ROOT / "dataset" / "task_summary.json"
OUTPUT_CSV = ROOT / "analysis" / "task_change_mechanism_classification_203.csv"
OUTPUT_JSON = ROOT / "analysis" / "task_change_mechanism_summary_203.json"
OUTPUT_MD = ROOT / "analysis" / "task_change_mechanism_taxonomy_203.md"

EXPECTED_TASK_COUNT = 203
EXPECTED_TASK_ORDER_SHA256 = (
    "c2da6aa10bb9fbd26b6e8871c3c92472253fc88fd1aef6675d4c995d7bb7c3e8"
)

MECHANISMS = {
    "package-module-namespace": {
        "scope": "direct",
        "description": "Package, module, import path, namespace, or export relocation.",
    },
    "api-symbol-removal-rename": {
        "scope": "direct",
        "description": "A dependency API symbol was removed, renamed, or replaced.",
    },
    "function-signature-calling-convention": {
        "scope": "direct",
        "description": "Arguments, return values, constructors, sync/async use, or call protocol changed.",
    },
    "type-interface-schema": {
        "scope": "direct",
        "description": "A dependency-exposed type, interface, field, generic, or schema shape changed.",
    },
    "runtime-semantic-behavior": {
        "scope": "indirect",
        "description": "The callable surface remained usable but runtime meaning or behavior changed.",
    },
    "dependency-chain-resolution": {
        "scope": "indirect",
        "description": "A transitive dependency, resolution result, bundled component, or interaction changed.",
    },
    "configuration-build-tooling": {
        "scope": "indirect",
        "description": "Configuration, compiler/linter policy, build system, test runner, or packaging changed.",
    },
    "generated-output-data-contract": {
        "scope": "indirect",
        "description": "Generated code, serialized data, SQL, formatting, snapshots, or textual output changed.",
    },
}

# Labels follow dataset/task_summary.json order. The task-order digest above prevents
# silent reassignment if that file is reordered or replaced.
LABEL_CODES = """
AR FS RS PN AR RS CB FS FS FS
GO TS AR TS TS GO CB AR FS CB
DR DR TS DR RS AR TS AR GO RS
AR AR TS AR AR RS RS CB CB AR
TS AR TS FS FS AR PN FS PN RS
FS TS TS TS PN PN AR AR PN DR
PN GO GO GO GO GO AR FS AR RS
AR AR TS PN FS FS PN GO CB CB
FS CB AR TS TS DR AR TS AR FS
FS AR FS AR AR PN GO DR AR RS
CB AR PN PN FS AR RS RS AR RS
PN PN PN CB AR AR AR CB AR AR
AR PN TS TS AR TS PN AR TS TS
PN AR FS AR AR PN TS TS CB FS
TS PN GO AR TS TS PN AR RS CB
FS GO RS GO GO GO TS RS FS PN
PN RS CB FS TS AR TS PN PN TS
CB RS PN RS TS PN TS CB FS AR
PN PN FS FS AR FS TS TS PN AR
AR PN PN CB TS TS RS PN TS CB
FS RS TS
""".split()

CODE_TO_MECHANISM = {
    "PN": "package-module-namespace",
    "AR": "api-symbol-removal-rename",
    "FS": "function-signature-calling-convention",
    "TS": "type-interface-schema",
    "RS": "runtime-semantic-behavior",
    "DR": "dependency-chain-resolution",
    "CB": "configuration-build-tooling",
    "GO": "generated-output-data-contract",
}


def percentage(count: int, total: int) -> float:
    return round(100 * count / total, 1)


def load_rows() -> list[dict[str, str]]:
    rows = json.loads(TASK_SUMMARY.read_text())
    if len(rows) != EXPECTED_TASK_COUNT:
        raise ValueError(f"expected {EXPECTED_TASK_COUNT} tasks, found {len(rows)}")
    if len(LABEL_CODES) != EXPECTED_TASK_COUNT:
        raise ValueError(
            f"expected {EXPECTED_TASK_COUNT} labels, found {len(LABEL_CODES)}"
        )

    task_order = "".join(f"{row['folder']}\n" for row in rows)
    digest = hashlib.sha256(task_order.encode()).hexdigest()
    if digest != EXPECTED_TASK_ORDER_SHA256:
        raise ValueError(f"task order digest changed: {digest}")

    classified = []
    for row, code in zip(rows, LABEL_CODES, strict=True):
        mechanism = CODE_TO_MECHANISM[code]
        classified.append(
            {
                "task": row["folder"],
                "ecosystem": row["ecosystem"],
                "library": row["library"],
                "old_version": row["old_version"],
                "new_version": row["new_version"],
                "primary_scope": MECHANISMS[mechanism]["scope"],
                "primary_mechanism": mechanism,
            }
        )
    return classified


def write_csv(rows: list[dict[str, str]]) -> None:
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_CSV.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def build_summary(rows: list[dict[str, str]]) -> dict:
    total = len(rows)
    scope_counts = Counter(row["primary_scope"] for row in rows)
    mechanism_counts = Counter(row["primary_mechanism"] for row in rows)
    ecosystem_counts: dict[str, Counter] = defaultdict(Counter)
    for row in rows:
        ecosystem_counts[row["ecosystem"]][row["primary_scope"]] += 1

    return {
        "benchmark_tasks": total,
        "classification_rule": (
            "Classify by the dominant oracle-repair mechanism. Direct means the "
            "first-order dependency's visible package/API/signature/type surface "
            "changed. Indirect means behavior, dependency resolution, configuration/"
            "tooling, or generated output changed without a primary first-order API "
            "surface break."
        ),
        "evidence_basis": [
            "dependency manifest and task metadata",
            "oracle solution patch",
            "hidden test patch and verifier witness",
        ],
        "scope_counts": [
            {
                "scope": scope,
                "count": scope_counts[scope],
                "percentage": percentage(scope_counts[scope], total),
            }
            for scope in ("direct", "indirect")
        ],
        "mechanism_counts": [
            {
                "scope": data["scope"],
                "mechanism": mechanism,
                "count": mechanism_counts[mechanism],
                "percentage": percentage(mechanism_counts[mechanism], total),
                "description": data["description"],
            }
            for mechanism, data in MECHANISMS.items()
        ],
        "scope_by_ecosystem": [
            {
                "ecosystem": ecosystem,
                "direct": counts["direct"],
                "indirect": counts["indirect"],
                "total": counts["direct"] + counts["indirect"],
            }
            for ecosystem, counts in sorted(ecosystem_counts.items())
        ],
    }


def write_markdown(summary: dict) -> None:
    scopes = {row["scope"]: row for row in summary["scope_counts"]}
    lines = [
        "# Task Change Mechanism Classification (203 Tasks)",
        "",
        "## Classification rule",
        "",
        summary["classification_rule"],
        "",
        "Each task receives one mutually exclusive primary label. Mixed tasks are",
        "classified by the mechanism that dominates the oracle repair.",
        "",
        "## Direct vs. indirect",
        "",
        "| Scope | Tasks | Share |",
        "| --- | ---: | ---: |",
        f"| Direct | {scopes['direct']['count']} | {scopes['direct']['percentage']:.1f}% |",
        f"| Indirect | {scopes['indirect']['count']} | {scopes['indirect']['percentage']:.1f}% |",
        f"| Total | {summary['benchmark_tasks']} | 100.0% |",
        "",
        "## Primary mechanisms",
        "",
        "| Scope | Mechanism | Tasks | Share |",
        "| --- | --- | ---: | ---: |",
    ]
    for row in summary["mechanism_counts"]:
        lines.append(
            f"| {row['scope'].title()} | `{row['mechanism']}` | "
            f"{row['count']} | {row['percentage']:.1f}% |"
        )

    lines.extend(
        [
            "",
            "## Definitions",
            "",
        ]
    )
    for mechanism, data in MECHANISMS.items():
        lines.append(
            f"- **{data['scope'].title()} / `{mechanism}`:** {data['description']}"
        )

    lines.extend(
        [
            "",
            "## Evidence and caveat",
            "",
            "The labels were reviewed against the dependency metadata, oracle repair",
            "patch, and hidden-test/verifier witness. They describe the primary repair",
            "mechanism, not every secondary effect present in a task.",
            "",
            "The task-level labels are in",
            "`analysis/task_change_mechanism_classification_203.csv`.",
            "",
        ]
    )
    OUTPUT_MD.write_text("\n".join(lines))


def main() -> None:
    rows = load_rows()
    write_csv(rows)
    summary = build_summary(rows)
    OUTPUT_JSON.write_text(json.dumps(summary, indent=2) + "\n")
    write_markdown(summary)
    print(
        json.dumps(
            {
                "tasks": len(rows),
                "scope_counts": summary["scope_counts"],
                "outputs": [str(OUTPUT_CSV), str(OUTPUT_JSON), str(OUTPUT_MD)],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
