"""Analysis: join the two annotators' per-trial labels and report inter-annotator
agreement — one headline κ per dimension (L/D/P/F) plus confusion + disagreements.

    python3 scripts/traj_analysis/agreement.py                      # latest index
    python3 scripts/traj_analysis/agreement.py --index jobs/trajannot-index-<tag>.json

Writes:
    harbor_benchmark/reports/traj_annotation_agreement_<date>.csv
    harbor_benchmark/reports/traj_annotation_agreement_<date>.md
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import common  # noqa: E402

# headline label per dimension: (record key, scale, universe, denominator predicate)
DIMENSIONS = [
    ("L leakage", "leakage_label", "ordinal", common.LEAKAGE_LABELS, lambda r: True),
    ("D evidence-mode", "evidence_gathering_mode", "nominal", common.EVIDENCE_MODES, lambda r: True),
    ("P alignment", "alignment_label", "nominal", common.ALIGNMENT_LABELS, lambda r: r == 1.0),
    ("F failure-cat", "failure_category_primary", "nominal", common.FAILURE_CATEGORIES, lambda r: r == 0.0),
]


def latest_index(jobs_dir: Path) -> Path:
    cands = sorted(jobs_dir.glob("trajannot-index-*.json"))
    if not cands:
        sys.exit(f"no trajannot-index-*.json under {jobs_dir}")
    return cands[-1]


def load_records(index: dict, label: str) -> dict[str, dict]:
    """key -> scoring record (via the robust loader)."""
    info = index["annotators"][label]
    out: dict[str, dict] = {}
    for key, t in index["trials"][label].items():
        meta = {
            "trial": key, "task": t.get("task"), "harness": None, "model": None,
            "reward": t.get("reward"),
        }
        out[key] = common.load_annotation(
            meta=meta,
            job_out_path=Path(t["job_out_path"]),
            trial_dir=Path(t["harbor_trial_dir"]),
            stage_dir=Path(t["stage_dir"]),
            agent_output_name=t.get("agent_output_name", info.get("agent_output_name", "agent.txt")),
        )
    return out


def md_table(headers: list[str], rows: list[list[str]]) -> str:
    line = "| " + " | ".join(headers) + " |"
    sep = "| " + " | ".join("---" for _ in headers) + " |"
    body = "\n".join("| " + " | ".join(r) + " |" for r in rows)
    return "\n".join([line, sep, body])


def fk(x) -> str:
    return "n/a" if x != x else f"{x:.3f}"  # NaN check


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--index", default=None)
    ap.add_argument("--jobs-dir", default="jobs")
    ap.add_argument("--out-dir", default="harbor_benchmark/reports")
    args = ap.parse_args()

    jobs_dir = (REPO_ROOT / args.jobs_dir).resolve()
    index_path = Path(args.index).resolve() if args.index else latest_index(jobs_dir)
    index = json.loads(index_path.read_text())
    annotators = list(index["annotators"].keys())
    if len(annotators) < 2:
        sys.exit(f"need 2 annotators for agreement, index has: {annotators}")
    a, b = annotators[0], annotators[1]
    keys = list(index["trials"][a].keys())

    da, db = load_records(index, a), load_records(index, b)

    out_dir = (REPO_ROOT / args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    csv_path = out_dir / f"traj_annotation_agreement_{date}.csv"
    md_path = out_dir / f"traj_annotation_agreement_{date}.md"

    # ---- per-trial rows + CSV
    rows = []
    for key in keys:
        ra, rb = da.get(key, {}), db.get(key, {})
        row = {
            "key": key,
            "task": ra.get("task") or rb.get("task") or "",
            "reward": ra.get("reward") if ra.get("reward") is not None else rb.get("reward"),
            f"{a}_parse": ra.get("parse_status", "missing"),
            f"{b}_parse": rb.get("parse_status", "missing"),
        }
        for _, field, _scale, _univ, _pred in DIMENSIONS:
            row[f"{a}_{field}"] = ra.get(field, "")
            row[f"{b}_{field}"] = rb.get(field, "")
        rows.append(row)
    with csv_path.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    # ---- agreement per dimension
    md = []
    md.append(f"# Trajectory Annotation — Inter-Annotator Agreement ({a} vs {b})\n")
    md.append(f"Date: {date} · Index: `{index_path.name}` · Trials: {len(keys)}")
    md.append(f"- {a}: `{index['annotators'][a]['model']}`")
    md.append(f"- {b}: `{index['annotators'][b]['model']}`")
    skipped = index.get("skipped_no_trajectory") or []
    md.append(f"- skipped (no trajectory): {len(skipped)}\n")

    head_rows = []
    for name, field, scale, universe, pred in DIMENSIONS:
        pairs = [
            (r[f"{a}_{field}"], r[f"{b}_{field}"])
            for r in rows if pred(r["reward"])
        ]
        m = common.percent_and_kappa(pairs)
        wk = common.weighted_kappa(pairs, universe) if scale == "ordinal" else float("nan")
        ac1 = common.gwet_ac1(pairs)
        pab = common.pabak(pairs, len(universe))
        head_rows.append([
            name, scale, str(m["n"]), fk(m["percent_agreement"]),
            fk(m["kappa"]), fk(wk) if scale == "ordinal" else "—", fk(ac1), fk(pab),
        ])
    md.append("## Headline agreement (one κ per dimension)\n")
    md.append(md_table(
        ["Dimension", "scale", "n scored", "% agree", "Cohen κ", "weighted κ", "Gwet AC1", "PABAK"],
        head_rows,
    ))
    md.append("")

    # ---- parse status
    pa_c = Counter(r[f"{a}_parse"] for r in rows)
    pb_c = Counter(r[f"{b}_parse"] for r in rows)
    md.append("## Parse status (ok=clean annotation.json, json_repaired=recovered, missing)\n")
    md.append(md_table(
        ["Annotator", "ok", "json_repaired", "missing", "total"],
        [[a, str(pa_c["ok"]), str(pa_c["json_repaired"]), str(pa_c["missing"]), str(sum(pa_c.values()))],
         [b, str(pb_c["ok"]), str(pb_c["json_repaired"]), str(pb_c["missing"]), str(sum(pb_c.values()))]],
    ))
    md.append("")

    # ---- confusion matrices + disagreements per dimension
    for name, field, _scale, universe, pred in DIMENSIONS:
        pairs = [(r[f"{a}_{field}"], r[f"{b}_{field}"]) for r in rows if pred(r["reward"])]
        conf = common.confusion_matrix(pairs, universe)
        cm_labels = [l for l in conf.keys() if any(conf[l].values()) or any(conf[x][l] for x in conf)]
        if not cm_labels:
            continue
        md.append(f"## {name}: confusion (rows = {a}, cols = {b})\n")
        md.append(md_table(
            [f"{a} \\ {b}"] + cm_labels,
            [[ra] + [str(conf[ra][cb]) for cb in cm_labels] for ra in cm_labels],
        ))
        md.append("")
        dis = [r for r in rows if pred(r["reward"])
               and r[f"{a}_{field}"] and r[f"{b}_{field}"]
               and r[f"{a}_{field}"] != r[f"{b}_{field}"]]
        if dis:
            md.append(f"### {name} disagreements ({len(dis)})\n")
            md.append(md_table(
                ["key", a, b],
                [[r["key"], r[f"{a}_{field}"], r[f"{b}_{field}"]] for r in dis[:50]],
            ))
            md.append("")

    md.append(f"Full per-trial labels: `{csv_path.relative_to(REPO_ROOT)}`\n")
    md_path.write_text("\n".join(md))

    # ---- console summary
    print(f"trials={len(keys)}  {a}_parse={dict(pa_c)}  {b}_parse={dict(pb_c)}")
    for r in head_rows:
        print(f"{r[0]:<18} n={r[2]:>4}  %agree={r[3]}  κ={r[4]}  wκ={r[5]}  AC1={r[6]}")
    print(f"wrote {csv_path}")
    print(f"wrote {md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
