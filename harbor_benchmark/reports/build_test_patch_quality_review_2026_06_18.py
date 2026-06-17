#!/usr/bin/env python3
"""Build and validate the full DepBench test-patch quality audit report."""

from __future__ import annotations

import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REPORTS = ROOT / "harbor_benchmark" / "reports"
TASK_SUMMARY = ROOT / "harbor_benchmark" / "task_summary.json"
CASES_DIR = REPORTS / "test_patch_quality_review_2026-06-18_cases"
OLD_CASES_DIR = REPORTS / "test_patch_quality_review_2026-06-17_cases"
CSV_PATH = REPORTS / "test_patch_quality_review_2026-06-18_cases.csv"
REPORT_PATH = REPORTS / "test_patch_quality_review_2026-06-18_full297.md"

VALID_VERDICTS = {
    "WITNESSES_BREAKING_CHANGE",
    "UNWITNESSED",
    "TESTS_OTHER_THING",
    "INCONCLUSIVE",
}

VALID_DC_NATURES = {
    "REAL_SOURCE_REPAIR",
    "FORMATTER_LINT_CHURN",
    "CONFIG_INFRA_ONLY",
    "TEST_ONLY",
    "SNAPSHOT_ONLY",
    "DOCS_EXAMPLE_ONLY",
    "MIXED",
}

VERDICT_ORDER = [
    "WITNESSES_BREAKING_CHANGE",
    "UNWITNESSED",
    "TESTS_OTHER_THING",
    "INCONCLUSIVE",
]

DC_ORDER = [
    "REAL_SOURCE_REPAIR",
    "FORMATTER_LINT_CHURN",
    "CONFIG_INFRA_ONLY",
    "TEST_ONLY",
    "SNAPSHOT_ONLY",
    "DOCS_EXAMPLE_ONLY",
    "MIXED",
]


def read(path: Path) -> str:
    return path.read_text(errors="replace")


def pct(n: int, d: int) -> str:
    return "0.0%" if d == 0 else f"{(100.0 * n / d):.1f}%"


def parse_bullet(text: str, label: str) -> str:
    m = re.search(rf"^- {re.escape(label)}:\s*(.*)$", text, re.M)
    return m.group(1).strip() if m else ""


def parse_section_value(text: str, section_number: str, valid: set[str]) -> str:
    m = re.search(
        rf"^## {re.escape(section_number)}\..*?\n(?P<body>.*?)(?=^## |\Z)",
        text,
        re.M | re.S,
    )
    if not m:
        return ""
    body = m.group("body")
    matches = [
        (match.start(), value)
        for value in valid
        if (match := re.search(rf"\b{re.escape(value)}\b", body))
    ]
    if matches:
        return min(matches)[1]
    return ""


def first_sentence(section: str) -> str:
    compact = " ".join(line.strip() for line in section.splitlines() if line.strip())
    if not compact:
        return ""
    return compact[:300]


def parse_section(text: str, section_number: str) -> str:
    m = re.search(
        rf"^## {re.escape(section_number)}\..*?\n(?P<body>.*?)(?=^## |\Z)",
        text,
        re.M | re.S,
    )
    return m.group("body").strip() if m else ""


def load_flagged_from_problematic_review() -> set[str]:
    path = REPORTS / "problematic_prs_review_2026-06-10.md"
    if not path.exists():
        return set()
    text = read(path)
    return set(re.findall(r"`([A-Za-z0-9_.-]+__[A-Za-z0-9_.-]+__\d+)`", text))


def parse_case(path: Path, summary: dict[str, dict], flagged_set: set[str]) -> dict:
    text = read(path)
    folder = path.stem
    meta = summary.get(folder, {})
    verdict = parse_section_value(text, "5", VALID_VERDICTS)
    dc_nature = parse_section_value(text, "6", VALID_DC_NATURES)
    flagged_text = parse_bullet(text, "Flagged in problematic_prs_review_2026-06-10.md")
    flagged = "YES" if flagged_text.upper().startswith("YES") or folder in flagged_set else "NO"
    upgrade = parse_bullet(text, "Upgrade")
    if not upgrade and meta:
        upgrade = f"{meta.get('library', '')} {meta.get('old_version', '')} -> {meta.get('new_version', '')}"
    test_cmd = parse_bullet(text, "test_cmd")
    return {
        "folder": folder,
        "ecosystem": parse_bullet(text, "Ecosystem") or meta.get("ecosystem", ""),
        "library": meta.get("library", ""),
        "old_version": meta.get("old_version", ""),
        "new_version": meta.get("new_version", ""),
        "upgrade": upgrade,
        "flagged": flagged,
        "test_cmd": test_cmd,
        "verdict": verdict,
        "dc_nature": dc_nature,
        "breaking_change_summary": first_sentence(parse_section(text, "2")),
        "test_patch_summary": first_sentence(parse_section(text, "3")),
        "direct_exercise_summary": first_sentence(parse_section(text, "4")),
        "notes": first_sentence(parse_section(text, "7")),
        "path": str(path.relative_to(ROOT)),
    }


def validate(rows: list[dict], summary: dict[str, dict]) -> list[str]:
    errors: list[str] = []
    expected = set(summary)
    observed = {r["folder"] for r in rows}
    missing = sorted(expected - observed)
    extra = sorted(observed - expected)
    if missing:
        errors.append(f"Missing case reports: {', '.join(missing[:20])}" + (" ..." if len(missing) > 20 else ""))
    if extra:
        errors.append(f"Unexpected case reports: {', '.join(extra[:20])}" + (" ..." if len(extra) > 20 else ""))
    for row in rows:
        if row["verdict"] not in VALID_VERDICTS:
            errors.append(f"{row['folder']}: invalid or missing verdict: {row['verdict']!r}")
        if row["dc_nature"] not in VALID_DC_NATURES:
            errors.append(f"{row['folder']}: invalid or missing Δc nature: {row['dc_nature']!r}")
        if not row["test_cmd"]:
            errors.append(f"{row['folder']}: missing test_cmd")
    return errors


def table_from_counter(counter: Counter, order: list[str] | None = None, total: int | None = None) -> str:
    total = total if total is not None else sum(counter.values())
    keys = order or sorted(counter)
    lines = ["| Value | Count | % |", "|---|---:|---:|"]
    for key in keys:
        if key in counter:
            lines.append(f"| `{key}` | {counter[key]} | {pct(counter[key], total)} |")
    return "\n".join(lines)


def cross_table(rows: list[dict], row_key: str, col_key: str, col_order: list[str]) -> str:
    grouped: dict[str, Counter] = defaultdict(Counter)
    totals = Counter()
    for row in rows:
        grouped[row[row_key]][row[col_key]] += 1
        totals[row[row_key]] += 1
    header = "| " + row_key.replace("_", " ").title() + " | Total | " + " | ".join(col_order) + " |"
    sep = "|---|---:|" + "|".join("---:" for _ in col_order) + "|"
    lines = [header, sep]
    for key in sorted(grouped):
        vals = [str(grouped[key].get(col, 0)) for col in col_order]
        lines.append(f"| {key} | {totals[key]} | " + " | ".join(vals) + " |")
    return "\n".join(lines)


def write_csv(rows: list[dict]) -> None:
    fields = [
        "folder",
        "ecosystem",
        "library",
        "old_version",
        "new_version",
        "upgrade",
        "flagged",
        "test_cmd",
        "verdict",
        "dc_nature",
        "breaking_change_summary",
        "test_patch_summary",
        "direct_exercise_summary",
        "notes",
        "path",
    ]
    with CSV_PATH.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows({k: row.get(k, "") for k in fields} for row in rows)


def old_sample_counts() -> tuple[Counter, Counter]:
    verdicts: Counter = Counter()
    dcs: Counter = Counter()
    if not OLD_CASES_DIR.exists():
        return verdicts, dcs
    for path in OLD_CASES_DIR.glob("*.md"):
        text = read(path)
        verdicts[parse_section_value(text, "5", VALID_VERDICTS)] += 1
        dcs[parse_section_value(text, "6", VALID_DC_NATURES)] += 1
    verdicts.pop("", None)
    dcs.pop("", None)
    return verdicts, dcs


def report(rows: list[dict]) -> str:
    total = len(rows)
    verdicts = Counter(r["verdict"] for r in rows)
    dcs = Counter(r["dc_nature"] for r in rows)
    ecosystems = Counter(r["ecosystem"] for r in rows)
    flagged = [r for r in rows if r["flagged"] == "YES"]
    non_flagged = [r for r in rows if r["flagged"] != "YES"]
    quarantine = [r for r in rows if r["verdict"] != "WITNESSES_BREAKING_CHANGE"]
    high_priority = [
        r
        for r in rows
        if r["verdict"] == "INCONCLUSIVE"
        or r["dc_nature"] in {"TEST_ONLY", "SNAPSHOT_ONLY", "DOCS_EXAMPLE_ONLY", "CONFIG_INFRA_ONLY"}
        or any(
            token in (r["notes"] + " " + r["direct_exercise_summary"]).lower()
            for token in ["wrong", "unpassable", "circular", "misattributed", "dead weight", "lint", "placeholder"]
        )
    ]
    old_verdicts, old_dcs = old_sample_counts()

    lines = [
        "# Test-Patch Quality Audit — Full 297 Tasks — 2026-06-18",
        "",
        "**Scope:** all 297 tasks in `harbor_benchmark/tasks_v4/`.",
        "**Method:** static expert review of `Δm` (manifest), `Δc` (oracle code patch), `Δt` (hidden test patch), and verifier `test_cmd`; 65 prior reports were reused as fixed prior work and 232 reports were newly produced.",
        "**Per-case details:** `harbor_benchmark/reports/test_patch_quality_review_2026-06-18_cases/<folder>.md`.",
        "**Machine-readable table:** `harbor_benchmark/reports/test_patch_quality_review_2026-06-18_cases.csv`.",
        "",
        "## 1. Executive Summary",
        "",
        f"Of {total} packaged DepBench tasks, **{verdicts['WITNESSES_BREAKING_CHANGE']} ({pct(verdicts['WITNESSES_BREAKING_CHANGE'], total)}) statically appear to witness the dependency breaking change** under the locked Level-1 definition. The remaining tasks should be treated as latent, testing another property, or needing manual/dynamic revalidation rather than being counted in the main witnessed benchmark headline.",
        "",
        table_from_counter(verdicts, VERDICT_ORDER, total),
        "",
        f"Main witnessed benchmark size after excluding latent/test-other/inconclusive cases: **{verdicts['WITNESSES_BREAKING_CHANGE']} / {total}**.",
        "",
        "## 2. Counts by Ecosystem",
        "",
        cross_table(rows, "ecosystem", "verdict", VERDICT_ORDER),
        "",
        "Ecosystem totals:",
        "",
        table_from_counter(ecosystems, total=total),
        "",
        "## 3. Counts by Δc Nature",
        "",
        table_from_counter(dcs, DC_ORDER, total),
        "",
        "Δc nature by verdict:",
        "",
        cross_table(rows, "dc_nature", "verdict", VERDICT_ORDER),
        "",
        "## 4. Flagged vs Non-Flagged Comparison",
        "",
        f"Problematic-review flagged cases in the full packaged set: **{len(flagged)}**. Non-flagged cases: **{len(non_flagged)}**.",
        "",
        "Flagged verdicts:",
        "",
        table_from_counter(Counter(r["verdict"] for r in flagged), VERDICT_ORDER, max(len(flagged), 1)),
        "",
        "Non-flagged verdicts:",
        "",
        table_from_counter(Counter(r["verdict"] for r in non_flagged), VERDICT_ORDER, max(len(non_flagged), 1)),
        "",
        "## 5. Comparison Against 65-Case Smoke Audit",
        "",
        "The earlier 65-case smoke audit reported this verdict distribution:",
        "",
        table_from_counter(old_verdicts, VERDICT_ORDER, sum(old_verdicts.values())),
        "",
        "The full-297 audit distribution is:",
        "",
        table_from_counter(verdicts, VERDICT_ORDER, total),
        "",
        "The smoke audit correctly predicted that npm/yarn dev-tooling, lint/formatter, and weak runtime-only test commands dominate the soundness gap; the full audit provides the actual packaged-dataset counts rather than the earlier extrapolation.",
        "",
        "## 6. Quarantine Candidates",
        "",
        f"These {len(quarantine)} cases are not currently clean Level-1 witnessed cases and should be excluded from the main witnessed benchmark until repaired or dynamically revalidated:",
        "",
        "| Folder | Ecosystem | Verdict | Δc Nature | Reason summary |",
        "|---|---|---|---|---|",
    ]
    for row in sorted(quarantine, key=lambda r: (r["verdict"], r["ecosystem"], r["folder"])):
        reason = (row["direct_exercise_summary"] or row["notes"] or row["breaking_change_summary"]).replace("|", "\\|")
        lines.append(f"| `{row['folder']}` | {row['ecosystem']} | `{row['verdict']}` | `{row['dc_nature']}` | {reason[:220]} |")

    lines.extend(
        [
            "",
            "## 7. High-Priority Manual/Dynamic Revalidation Cases",
            "",
            "These cases deserve first manual or dynamic checks because the static evidence is inconclusive or the patch shape suggests a benchmark-design defect:",
            "",
            "| Folder | Ecosystem | Verdict | Δc Nature | Notes |",
            "|---|---|---|---|---|",
        ]
    )
    for row in sorted(high_priority, key=lambda r: (r["verdict"], r["dc_nature"], r["folder"])):
        note = (row["notes"] or row["direct_exercise_summary"] or row["breaking_change_summary"]).replace("|", "\\|")
        lines.append(f"| `{row['folder']}` | {row['ecosystem']} | `{row['verdict']}` | `{row['dc_nature']}` | {note[:220]} |")

    lines.extend(
        [
            "",
            "## 8. Methodology and Limitations",
            "",
            "Each task was reviewed from a bundle containing `instruction.md`, `manifest.patch`, `solution/code.patch`, `tests/test.patch`, `tests/test_state.py`, extracted `test_cmd`, and `task_summary.json` metadata. Reviewers answered the same seven questions used in the 2026-06-17 smoke audit.",
            "",
            "The classification is static. `WITNESSES_BREAKING_CHANGE` means the patch evidence strongly indicates `TEST(P⊕Δm⊕Δt)=FAIL` and `TEST(P⊕Δm⊕Δc⊕Δt)=PASS`; it is not a replacement for the dynamic pre-code witness check that should gate future packaging. `INCONCLUSIVE` means the static evidence was insufficient and the case needs a targeted Harbor trial or manual reproduction.",
            "",
            "Locked exclusions are preserved: dependency-resolution failures, network/environment/OOM/timeouts/flakiness, and lint/format-only checks are not Level-1 breaking-change witnesses even if they produce a non-zero verifier exit.",
            "",
            "## 9. Implications for Paper Numbers and Benchmark Reporting",
            "",
            f"The headline full packaged dataset remains 297 tasks, but the main witnessed benchmark should report **{verdicts['WITNESSES_BREAKING_CHANGE']} clean Level-1 cases** unless the excluded cases are repaired and dynamically revalidated. Latent and test-other cases should be characterized separately as evidence about mining noise and test-oracle sensitivity, not agent repair difficulty.",
            "",
            "For paper tables, keep separate rows for: packaged total, witnessed Level-1, latent/unwitnessed, tests-other, and inconclusive/manual-revalidation. This prevents the benchmark headline from mixing direct dependency-update repair tasks with formatter/lint migrations, weak tests, or unrelated PR drive-by changes.",
            "",
            "## 10. Case Reports Index",
            "",
            "| Folder | Ecosystem | Verdict | Δc Nature | Flagged |",
            "|---|---|---|---|---|",
        ]
    )
    for row in sorted(rows, key=lambda r: r["folder"].lower()):
        lines.append(f"| `{row['folder']}` | {row['ecosystem']} | `{row['verdict']}` | `{row['dc_nature']}` | {row['flagged']} |")

    return "\n".join(lines) + "\n"


def main() -> int:
    summary_list = json.loads(read(TASK_SUMMARY))
    summary = {row["folder"]: row for row in summary_list}
    flagged_set = load_flagged_from_problematic_review()
    rows = [parse_case(path, summary, flagged_set) for path in sorted(CASES_DIR.glob("*.md"))]
    rows.sort(key=lambda r: r["folder"].lower())
    errors = validate(rows, summary)
    if errors:
        print("Audit validation failed:")
        for err in errors:
            print(f"- {err}")
        return 1
    write_csv(rows)
    REPORT_PATH.write_text(report(rows))
    print(f"Validated {len(rows)} case reports")
    print(f"Wrote {CSV_PATH}")
    print(f"Wrote {REPORT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
