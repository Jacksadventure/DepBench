#!/usr/bin/env python3
"""Generate a markdown report from the per-trial annotations sitting in the harbor_jobs
canonical dirs (annotation__<agent>.json). Works on partial results — labels each section
with the coverage it actually has. Reuses common.py for the agreement math.

    python3 scripts/traj_analysis/report.py
    python3 scripts/traj_analysis/report.py --agents codex,opencode --out harbor_benchmark/reports/...
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import common  # noqa: E402
import run_annotation as R  # noqa: E402


def load(agent: str, trials: list[dict]) -> dict[str, dict]:
    """key -> coerced record for trials that have annotation__<agent>.json."""
    out: dict[str, dict] = {}
    name = f"annotation__{agent}.json"
    for t in trials:
        p = t["trial_dir"] / name
        obj = common._try_json_file(p)
        if obj is None:
            continue
        rec = common.coerce_annotation(obj, t["meta"])
        rec["group"] = f"{t['meta'].get('harness') or '?'} / {t['meta'].get('model') or '?'}"
        out[t["key"]] = rec
    return out


def pct(n: int, d: int) -> str:
    return f"{100*n/d:.1f}%" if d else "—"


def dist_rows(recs: list[dict], field: str, universe: list[str]) -> list[list[str]]:
    c = Counter(r[field] for r in recs if r.get(field))
    n = sum(c.values())
    rows = [[lab, str(c.get(lab, 0)), pct(c.get(lab, 0), n)] for lab in universe]
    extra = sorted(set(c) - set(universe))
    rows += [[lab, str(c[lab]), pct(c[lab], n)] for lab in extra]
    return rows


def mdtable(headers, rows):
    line = "| " + " | ".join(headers) + " |"
    sep = "| " + " | ".join("---" for _ in headers) + " |"
    body = "\n".join("| " + " | ".join(map(str, r)) + " |" for r in rows)
    return "\n".join([line, sep, body])


def fk(x):
    return "n/a" if x != x else f"{x:.3f}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--agents", default="codex,opencode")
    ap.add_argument("--jobs-glob", default="harbor_jobs/v4_withtest219*")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    agents = [a.strip() for a in args.agents.split(",") if a.strip()]

    trials = [t for t in R.discover_trials([args.jobs_glob]) if t["meta"]["has_trajectory"]]
    data = {a: load(a, trials) for a in agents}
    date = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    md: list[str] = []
    md.append("# Trajectory Annotation — Interim Report\n")
    md.append(f"Generated: {date}  ·  eligible trials (have trajectory): **{len(trials)}**\n")

    # ---- coverage
    md.append("## 1. Coverage\n")
    cov = [[a, str(len(data[a])), pct(len(data[a]), len(trials))] for a in agents]
    both = sum(1 for t in trials if all(t["key"] in data[a] for a in agents))
    md.append(mdtable(["annotator", "annotated", "of eligible"], cov))
    md.append(f"\nTrials annotated by **all {len(agents)}**: {both} ({pct(both, len(trials))})\n")

    # per-group coverage (primary annotator = first)
    pa = agents[0]
    grp = defaultdict(lambda: [0, 0])
    for t in trials:
        g = f"{t['meta'].get('harness') or '?'} / {t['meta'].get('model') or '?'}"
        grp[g][0] += 1
        if t["key"] in data[pa]:
            grp[g][1] += 1
    md.append("\n### Per harness × LLM (annotated by " + pa + ")\n")
    md.append(mdtable(["group", "eligible", "annotated"],
                      [[g, e, a] for g, (e, a) in sorted(grp.items())]))
    md.append("")

    # ---- per-annotator distributions
    for i, a in enumerate(agents, start=1):
        recs = list(data[a].values())
        n = len(recs)
        md.append(f"## 2.{i} {a} ({n} trials) — label distributions\n")
        md.append("**Leakage** (L)\n")
        md.append(mdtable(["label", "n", "%"], dist_rows(recs, "leakage_label", common.LEAKAGE_LABELS)))
        leaked = sum(1 for r in recs if r["leakage_label"] in ("suspect", "confirmed"))
        conf = sum(1 for r in recs if r["leakage_label"] == "confirmed")
        md.append(f"\n→ **confirmed leakage: {conf} ({pct(conf, n)})**, incl. suspect: {leaked} ({pct(leaked, n)})\n")
        md.append("\n**RQ4 evidence-gathering mode** (D)\n")
        md.append(mdtable(["mode", "n", "%"], dist_rows(recs, "evidence_gathering_mode", common.EVIDENCE_MODES)))
        vis = sum(1 for r in recs if r.get("visible_then_hidden_overfit") is True)
        fails = sum(1 for r in recs if r["reward"] == 0.0)
        md.append(f"\nVisible-then-hidden overfit: {vis} (of {fails} failed = {pct(vis, fails)})\n")
        passes = [r for r in recs if r["reward"] == 1.0]
        md.append(f"\n**Pass alignment** (P) — {len(passes)} passing trials\n")
        md.append(mdtable(["label", "n", "%"], dist_rows(passes, "alignment_label", common.ALIGNMENT_LABELS)))
        fr = [r for r in recs if r["reward"] == 0.0]
        md.append(f"\n**Failure category** (F) — {len(fr)} failing trials\n")
        md.append(mdtable(["category", "n", "%"], dist_rows(fr, "failure_category_primary", common.FAILURE_CATEGORIES)))
        md.append("")

    # ---- agreement (first two annotators)
    if len(agents) >= 2:
        a, b = agents[0], agents[1]
        keys = [t["key"] for t in trials if t["key"] in data[a] and t["key"] in data[b]]
        md.append(f"## 3. Inter-annotator agreement ({a} vs {b}, n={len(keys)} co-annotated)\n")
        dims = [
            ("L leakage", "leakage_label", "ordinal", common.LEAKAGE_LABELS, lambda r: True),
            ("D evidence-mode", "evidence_gathering_mode", "nominal", common.EVIDENCE_MODES, lambda r: True),
            ("P alignment", "alignment_label", "nominal", common.ALIGNMENT_LABELS, lambda r: r == 1.0),
            ("F failure-cat", "failure_category_primary", "nominal", common.FAILURE_CATEGORIES, lambda r: r == 0.0),
        ]
        rows = []
        for name, field, scale, univ, pred in dims:
            pairs = [(data[a][k][field], data[b][k][field]) for k in keys
                     if pred(data[a][k]["reward"])]
            m = common.percent_and_kappa(pairs)
            wk = common.weighted_kappa(pairs, univ) if scale == "ordinal" else float("nan")
            ac1 = common.gwet_ac1(pairs)
            rows.append([name, str(m["n"]), fk(m["percent_agreement"]), fk(m["kappa"]),
                         fk(wk) if scale == "ordinal" else "—", fk(ac1)])
        md.append(mdtable(["dimension", "n", "% agree", "Cohen κ", "weighted κ", "Gwet AC1"], rows))
        md.append("")

    out = Path(args.out).resolve() if args.out else (
        REPO_ROOT / "harbor_benchmark" / "reports" /
        f"traj_annotation_report_{datetime.now(timezone.utc).strftime('%Y-%m-%d')}.md")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(md))
    print(f"wrote {out}")
    print(f"coverage: " + ", ".join(f"{a}={len(data[a])}" for a in agents) + f"  both={both}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
