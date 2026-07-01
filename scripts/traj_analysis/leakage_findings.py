#!/usr/bin/env python3
"""Extract a focused, human-inspectable list of the LEAKAGES found by the annotators.

For every trial labelled suspect/confirmed leak by either annotator, emit one row with the
task, outcome, leak vectors, and the exact leaked artifact (URL/host + the annotator's finding)
pulled from the `online_resources` observations. Writes CSV (for filtering) and Markdown (for
reading), plus a cross-annotator agreement column.

    python3 scripts/traj_analysis/leakage_findings.py
"""
from __future__ import annotations

import argparse
import csv
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import common  # noqa: E402
import run_annotation as R  # noqa: E402

AGENTS = ["codex", "opencode"]
OWN = {"own-pull-request", "own-commit-or-patch", "own-project-repo", "mirror-or-codesearch"}


def leaked_artifact(obj: dict) -> tuple[str, str, str]:
    """Best leaked URL/host/finding: prefer a resource that returned solution content."""
    res = (obj.get("observations") or {}).get("online_resources") or []
    pick = None
    for r in res:
        if r.get("returned_solution_content"):
            pick = r
            break
    if pick is None:
        for r in res:
            if (r.get("category") or "") in OWN:
                pick = r
                break
    if pick is None:
        return "", "", ""
    return pick.get("target", ""), pick.get("host", ""), (pick.get("finding", "") or "").replace("\n", " ")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default="harbor_benchmark/annotations/v4_withtest219_20260630")
    ap.add_argument("--jobs-glob", default="harbor_jobs/v4_withtest219*",
                    help="comma-separated jobs glob(s) to scan")
    ap.add_argument("--prefix", default="", help="output filename prefix, e.g. 'claude48_'")
    args = ap.parse_args()
    out_dir = (REPO_ROOT / args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    globs = [g.strip() for g in args.jobs_glob.split(",") if g.strip()]

    trials = [t for t in R.discover_trials(globs) if t["meta"]["has_trajectory"]]
    # label per (trial, annotator)
    labels: dict[str, dict[str, str]] = {}
    rows = []
    for t in trials:
        labels[t["key"]] = {}
        for a in AGENTS:
            obj = common._try_json_file(t["trial_dir"] / f"annotation__{a}.json")
            if obj is None:
                continue
            lk = obj.get("leakage") or {}
            lab = str(lk.get("label") or "")
            labels[t["key"]][a] = lab
            if lab in ("suspect", "confirmed"):
                url, host, finding = leaked_artifact(obj)
                rows.append({
                    "task": t["meta"]["task"], "key": t["key"],
                    "harness": t["meta"].get("harness"), "llm": t["meta"].get("model"),
                    "reward": t["meta"].get("reward"), "annotator": a, "label": lab,
                    "leak_vectors": "|".join(lk.get("leak_vectors") or []),
                    "retrieved_oracle": lk.get("retrieved_oracle"),
                    "leak_precedes_fix": lk.get("leak_precedes_fix"),
                    "confidence": lk.get("confidence", ""),
                    "leaked_url": url, "leaked_host": host, "finding": finding,
                })

    # cross-annotator agreement per task-trial
    def agree(key):
        v = labels.get(key, {})
        cl = {a: ("leak" if v.get(a) in ("suspect", "confirmed") else "clean" if v.get(a) else "-") for a in AGENTS}
        if cl["codex"] == "leak" and cl["opencode"] == "leak":
            return "both"
        if "leak" in cl.values() and "-" in cl.values():
            return "single-annotated"
        return "one-only"
    for r in rows:
        r["agreement"] = agree(r["key"])

    rows.sort(key=lambda r: (r["label"] != "confirmed", r["task"], r["annotator"]))
    cols = ["task", "harness", "llm", "reward", "annotator", "label", "agreement",
            "leak_vectors", "retrieved_oracle", "leak_precedes_fix", "confidence",
            "leaked_host", "leaked_url", "finding", "key"]
    csv_path = out_dir / f"{args.prefix}leakage_findings.csv"
    with csv_path.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)

    # markdown — confirmed first, grouped, readable
    confirmed = [r for r in rows if r["label"] == "confirmed"]
    suspect = [r for r in rows if r["label"] == "suspect"]
    both_conf = sorted({r["task"] for r in confirmed
                        if agree(r["key"]) == "both"})
    md = [f"# Leakage findings — v4-with-test219 (interim, {datetime.now(timezone.utc):%Y-%m-%d %H:%M UTC})\n"]
    md.append(f"Annotated so far: " + ", ".join(
        f"{a}={sum(1 for t in trials if labels[t['key']].get(a))}" for a in AGENTS) +
        f" / {len(trials)} eligible.\n")
    md.append(f"- **Confirmed-leak rows:** {len(confirmed)}  ·  **suspect rows:** {len(suspect)}")
    md.append(f"- **Tasks flagged confirmed by BOTH annotators:** {len(both_conf)}\n")

    def table(rs):
        head = "| task | harness/llm | reward | ann | agree | vectors | leaked artifact | finding |"
        sep = "|---|---|---|---|---|---|---|---|"
        body = []
        for r in rs:
            art = f"`{r['leaked_url']}`" if r["leaked_url"] else (r["leaked_host"] or "—")
            body.append(f"| {r['task']} | {r['harness']}/{r['llm']} | {r['reward']} | "
                        f"{r['annotator']} | {r['agreement']} | {r['leak_vectors']} | {art} | "
                        f"{(r['finding'] or '')[:160]} |")
        return "\n".join([head, sep, *body])

    md.append("## Confirmed leaks\n")
    md.append(table(confirmed))
    md.append("\n## Suspect leaks\n")
    md.append(table(suspect))
    (out_dir / f"{args.prefix}leakage_findings.md").write_text("\n".join(md) + "\n")

    print(f"wrote {csv_path}")
    print(f"wrote {out_dir / (args.prefix+'leakage_findings.md')}")
    print(f"rows: confirmed={len(confirmed)} suspect={len(suspect)} both-confirmed-tasks={len(both_conf)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
