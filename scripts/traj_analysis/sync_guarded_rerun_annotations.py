#!/usr/bin/env python3
"""Synchronize guarded rerun trajectory annotations into annotation JSONLs."""
from __future__ import annotations

import csv
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
ANN_DIR = REPO_ROOT / "harbor_benchmark/annotations/v4_withtest219_20260630"
REMAINING_REPORT = REPO_ROOT / "harbor_benchmark/reports/guarded_leak_remaining_claude_rerun_results_20260702.csv"
ANNOTATION_PREFIX = "annotation_guarded_rerun"
ANNOTATORS = ("codex", "opencode")


def normalize_harness(value: str) -> str:
    return {
        "claude_code": "claude-code",
        "claude-code": "claude-code",
        "copilot_cli": "copilot-cli",
        "copilot-cli": "copilot-cli",
        "opencode": "opencode",
        "codex": "codex",
    }.get(value, value)


def parse_reward(value: str) -> float | None:
    if value == "" or value is None:
        return None
    try:
        return float(value)
    except ValueError:
        return None


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows))


def trial_name(row: dict[str, str]) -> str:
    return Path(row["trial_dir"]).name


def row_key(row: dict[str, str]) -> str:
    return f"{Path(row['job_dir']).name}__{trial_name(row)}"


def load_annotation(row: dict[str, str], annotator: str) -> dict[str, Any] | None:
    path = REPO_ROOT / row["trial_dir"] / f"{ANNOTATION_PREFIX}__{annotator}.json"
    if not path.exists():
        return None
    try:
        obj = json.loads(path.read_text())
    except json.JSONDecodeError:
        return None
    if not isinstance(obj, dict) or not isinstance(obj.get("leakage"), dict):
        return None
    label = str(obj["leakage"].get("label") or "")
    if label == "no_leakage":
        obj["leakage"]["label"] = "none"
        label = "none"
    if label not in {"none", "suspect", "confirmed"}:
        return None
    return obj


def placeholder_annotation(row: dict[str, str], annotator: str, reason: str) -> dict[str, Any]:
    task = row["task"]
    harness = normalize_harness(row["harness"])
    llm = row["llm"]
    reward = parse_reward(row.get("reward", ""))
    return {
        "schema_version": "depbench-trajectory-annotation-v1",
        "annotator": annotator,
        "analyzable": False,
        "not_analyzable_reason": reason,
        "task": task,
        "trial": trial_name(row),
        "harness": harness,
        "llm": llm,
        "reward": reward,
        "leakage": {
            "label": "not_analyzable",
            "confidence": "low",
            "leak_vectors": [],
            "retrieved_oracle": None,
            "leak_precedes_fix": None,
            "summary": reason,
        },
        "discovery": {
            "evidence_gathering_mode": "none",
            "docs_lookup": "none",
            "visible_then_hidden_overfit": None,
        },
        "pass_alignment": {
            "alignment_label": "not_analyzable",
            "key_change_matches": None,
        },
        "failure": {
            "failure_category_primary": "infra-exception" if row.get("exception_type") else "not_analyzable",
            "distance_to_oracle": "not_analyzable",
            "summary": reason,
        },
        "observations": {"online_resources": []},
    }


def annotation_for(row: dict[str, str], annotator: str) -> tuple[dict[str, Any], str]:
    obj = load_annotation(row, annotator)
    status = "annotated"
    if obj is None:
        trial_dir = REPO_ROOT / row["trial_dir"]
        has_traj = (trial_dir / "agent/trajectory.json").exists()
        raw_logs = [p for p in (trial_dir / "agent").glob("*.txt") if p.stat().st_size > 0]
        reason = (
            "Guarded rerun has no agent trajectory/raw log; leakage and failure trajectory analysis cannot be performed."
            if not has_traj and not raw_logs
            else "Guarded rerun trajectory was available, but this annotator did not produce a valid annotation."
        )
        obj = placeholder_annotation(row, annotator, reason)
        status = "placeholder"

    task = row["task"]
    harness = normalize_harness(row["harness"])
    llm = row["llm"]
    reward = parse_reward(row.get("reward", ""))
    obj["task"] = task
    obj["trial"] = trial_name(row)
    obj["harness"] = harness
    obj["llm"] = llm
    obj["reward"] = reward
    if "analyzable" not in obj or obj["analyzable"] is None:
        obj["analyzable"] = True
    obj.setdefault("not_analyzable_reason", "")
    obj["guarded_rerun"] = {
        "source_job": Path(row["job_dir"]).name,
        "source_trial_dir": row["trial_dir"],
        "artifact_dir": row.get("artifact_dir", ""),
        "source_note": row.get("source_note", ""),
        "synced_at": datetime.now(timezone.utc).isoformat(),
    }
    return obj, status


def jsonl_row(row: dict[str, str], annotator: str) -> tuple[dict[str, Any], str]:
    annotation, status = annotation_for(row, annotator)
    return {
        "key": row_key(row),
        "task": row["task"],
        "harness": normalize_harness(row["harness"]),
        "llm": row["llm"],
        "reward": parse_reward(row.get("reward", "")),
        "annotation": annotation,
    }, status


def replace_rows(path: Path, replacements: list[dict[str, Any]]) -> dict[str, int]:
    rows = read_jsonl(path)
    by_tuple = {(r["task"], normalize_harness(r.get("harness") or ""), r["llm"]): r for r in replacements}
    seen: set[tuple[str, str, str]] = set()
    replaced = 0
    out: list[dict[str, Any]] = []
    for row in rows:
        key = (row["task"], normalize_harness(row.get("harness") or ""), row["llm"])
        replacement = by_tuple.get(key)
        if replacement:
            out.append(replacement)
            seen.add(key)
            replaced += 1
        else:
            out.append(row)
    added = 0
    for key, replacement in sorted(by_tuple.items()):
        if key not in seen:
            out.append(replacement)
            added += 1
    write_jsonl(path, out)
    return {"replaced": replaced, "added": added, "rows": len(out)}


def leaked_artifact(obj: dict[str, Any]) -> tuple[str, str, str]:
    resources = ((obj.get("observations") or {}).get("online_resources") or [])
    pick = None
    for item in resources:
        if item.get("returned_solution_content"):
            pick = item
            break
    if pick is None:
        own = {"own-pull-request", "own-commit-or-patch", "own-project-repo", "mirror-or-codesearch"}
        for item in resources:
            if (item.get("category") or "") in own:
                pick = item
                break
    if pick is None:
        return "", "", ""
    return pick.get("target", ""), pick.get("host", ""), (pick.get("finding", "") or "").replace("\n", " ")


def leakage_findings_from_jsonl(prefix: str, codex_path: Path, opencode_path: Path) -> dict[str, int]:
    files = {"codex": read_jsonl(codex_path), "opencode": read_jsonl(opencode_path)}
    labels: dict[str, dict[str, str]] = {}
    rows: list[dict[str, Any]] = []
    for annotator, anns in files.items():
        for row in anns:
            key = row["key"]
            labels.setdefault(key, {})
            ann = row.get("annotation") or {}
            leakage = ann.get("leakage") if isinstance(ann.get("leakage"), dict) else {}
            label = str(leakage.get("label") or "")
            labels[key][annotator] = label
            if label not in {"suspect", "confirmed"}:
                continue
            url, host, finding = leaked_artifact(ann)
            rows.append({
                "task": row.get("task"),
                "harness": row.get("harness"),
                "llm": row.get("llm"),
                "reward": row.get("reward"),
                "annotator": annotator,
                "label": label,
                "leak_vectors": "|".join(leakage.get("leak_vectors") or []),
                "retrieved_oracle": leakage.get("retrieved_oracle"),
                "leak_precedes_fix": leakage.get("leak_precedes_fix"),
                "confidence": leakage.get("confidence", ""),
                "leaked_host": host,
                "leaked_url": url,
                "finding": finding,
                "key": key,
            })

    def agreement(key: str) -> str:
        vals = labels.get(key, {})
        states = {a: "leak" if vals.get(a) in {"suspect", "confirmed"} else "clean" if a in vals else "-" for a in ANNOTATORS}
        if states["codex"] == "leak" and states["opencode"] == "leak":
            return "both"
        if "leak" in states.values() and "-" in states.values():
            return "single-annotated"
        return "one-only"

    for row in rows:
        row["agreement"] = agreement(row["key"])
    rows.sort(key=lambda r: (r["label"] != "confirmed", r["task"], r["annotator"]))

    cols = ["task", "harness", "llm", "reward", "annotator", "label", "agreement",
            "leak_vectors", "retrieved_oracle", "leak_precedes_fix", "confidence",
            "leaked_host", "leaked_url", "finding", "key"]
    csv_path = ANN_DIR / f"{prefix}leakage_findings.csv"
    with csv_path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=cols, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    confirmed = [r for r in rows if r["label"] == "confirmed"]
    suspect = [r for r in rows if r["label"] == "suspect"]
    both_conf = sorted({r["task"] for r in confirmed if r["agreement"] == "both"})
    md = [
        f"# Leakage findings — {prefix.rstrip('_') or 'v4-with-test219'} ({datetime.now(timezone.utc):%Y-%m-%d %H:%M UTC})",
        "",
        f"- **Confirmed-leak rows:** {len(confirmed)}",
        f"- **Suspect rows:** {len(suspect)}",
        f"- **Tasks flagged confirmed by BOTH annotators:** {len(both_conf)}",
        "",
        "| task | harness/llm | reward | ann | agree | vectors | leaked artifact | finding |",
        "|---|---|---:|---|---|---|---|---|",
    ]
    for row in confirmed + suspect:
        artifact = f"`{row['leaked_url']}`" if row["leaked_url"] else (row["leaked_host"] or "—")
        md.append(
            f"| {row['task']} | {row['harness']}/{row['llm']} | {row['reward']} | "
            f"{row['annotator']} | {row['agreement']} | {row['leak_vectors']} | {artifact} | "
            f"{(row['finding'] or '')[:160]} |"
        )
    (ANN_DIR / f"{prefix}leakage_findings.md").write_text("\n".join(md) + "\n")
    return {"confirmed": len(confirmed), "suspect": len(suspect), "both_confirmed_tasks": len(both_conf)}


def main() -> int:
    rows = list(csv.DictReader(REMAINING_REPORT.open()))
    by_group = {group: [r for r in rows if r["group"] == group] for group in {
        "claude_code_gemini",
        "claude_code_claude48",
        "opencode_claude48",
    }}

    summary: dict[str, Any] = {"generated_at": datetime.now(timezone.utc).isoformat(), "sources": [str(REMAINING_REPORT.relative_to(REPO_ROOT))]}
    for annotator in ANNOTATORS:
        gemini_rows = [jsonl_row(r, annotator)[0] for r in by_group["claude_code_gemini"]]
        gemini_path = ANN_DIR / f"guarded_claude_code_gemini_{annotator}.jsonl"
        write_jsonl(gemini_path, gemini_rows)
        statuses = Counter(jsonl_row(r, annotator)[1] for group in by_group.values() for r in group)
        claude48_replacements = [jsonl_row(r, annotator)[0] for r in by_group["claude_code_claude48"] + by_group["opencode_claude48"]]
        replace_stats = replace_rows(ANN_DIR / f"claude48_{annotator}.jsonl", claude48_replacements)
        summary[annotator] = {
            "guarded_claude_code_gemini_rows": len(gemini_rows),
            "claude48_replacements": replace_stats,
            "annotation_statuses": dict(statuses),
        }

    summary["claude48_leakage_findings"] = leakage_findings_from_jsonl(
        "claude48_",
        ANN_DIR / "claude48_codex.jsonl",
        ANN_DIR / "claude48_opencode.jsonl",
    )
    summary["guarded_claude_code_gemini_leakage_findings"] = leakage_findings_from_jsonl(
        "guarded_claude_code_gemini_",
        ANN_DIR / "guarded_claude_code_gemini_codex.jsonl",
        ANN_DIR / "guarded_claude_code_gemini_opencode.jsonl",
    )

    index_path = ANN_DIR / "index.json"
    index = json.loads(index_path.read_text())
    index["guarded_remaining_claude_annotation_sync"] = summary
    for filename in [
        "guarded_claude_code_gemini_codex.jsonl",
        "guarded_claude_code_gemini_opencode.jsonl",
        "guarded_claude_code_gemini_leakage_findings.csv",
        "guarded_claude_code_gemini_leakage_findings.md",
    ]:
        if filename not in index["files"]:
            index["files"].append(filename)
    index_path.write_text(json.dumps(index, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
