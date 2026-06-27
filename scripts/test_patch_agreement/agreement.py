"""Analysis: join the two agents' VERDICT.json labels and report agreement.

    python3 scripts/test_patch_agreement/agreement.py            # uses latest index
    python3 scripts/test_patch_agreement/agreement.py --index jobs/agreement-index-<tag>.json

Writes:
    harbor_benchmark/reports/test_patch_agreement_<date>.csv
    harbor_benchmark/reports/test_patch_agreement_<date>.md
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


def latest_index(jobs_dir: Path) -> Path:
    cands = sorted(jobs_dir.glob("agreement-index-*.json"))
    if not cands:
        sys.exit(f"no agreement-index-*.json under {jobs_dir}")
    return cands[-1]


def load_all(index: dict) -> dict[str, dict[str, dict]]:
    """agent -> task -> verdict record."""
    out: dict[str, dict[str, dict]] = {}
    for agent, info in index["agents"].items():
        out[agent] = {}
        for task, t in index["trials"][agent].items():
            out[agent][task] = common.load_verdict(
                task=task,
                trial_dir=Path(t["trial_dir"]),
                stage_dir=Path(t["stage_dir"]),
                agent_output_name=t.get("agent_output_name", info.get("output_name", "agent.txt")),
            )
    return out


def md_table(headers: list[str], rows: list[list[str]]) -> str:
    line = "| " + " | ".join(headers) + " |"
    sep = "| " + " | ".join("---" for _ in headers) + " |"
    body = "\n".join("| " + " | ".join(r) + " |" for r in rows)
    return "\n".join([line, sep, body])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--index", default=None)
    ap.add_argument("--jobs-dir", default="jobs")
    ap.add_argument("--out-dir", default="harbor_benchmark/reports")
    args = ap.parse_args()

    jobs_dir = (REPO_ROOT / args.jobs_dir).resolve()
    index_path = Path(args.index).resolve() if args.index else latest_index(jobs_dir)
    index = json.loads(index_path.read_text())
    agents = list(index["agents"].keys())
    if len(agents) < 2:
        sys.exit(f"need 2 agents for agreement, index has: {agents}")
    a, b = agents[0], agents[1]
    tasks = index["tasks"]

    data = load_all(index)
    out_dir = (REPO_ROOT / args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    csv_path = out_dir / f"test_patch_agreement_{date}.csv"
    md_path = out_dir / f"test_patch_agreement_{date}.md"

    # ---- per-task rows + CSV
    rows = []
    for task in tasks:
        ra = data[a].get(task, {})
        rb = data[b].get(task, {})
        va, vb = ra.get("verdict", ""), rb.get("verdict", "")
        ba = "WITNESS" if common.is_witness(va) else ("NOT" if va else "")
        bb = "WITNESS" if common.is_witness(vb) else ("NOT" if vb else "")
        rows.append({
            "task": task,
            f"{a}_verdict": va, f"{b}_verdict": vb,
            "agree_verdict": int(bool(va and vb and va == vb)),
            f"{a}_binary": ba, f"{b}_binary": bb,
            "agree_binary": int(bool(ba and bb and ba == bb)),
            f"{a}_category": ra.get("taxonomy_category", ""),
            f"{b}_category": rb.get("taxonomy_category", ""),
            f"{a}_dc_nature": ra.get("delta_c_nature", ""),
            f"{b}_dc_nature": rb.get("delta_c_nature", ""),
            f"{a}_import_only": ra.get("import_only_delta_t"),
            f"{b}_import_only": rb.get("import_only_delta_t"),
            f"{a}_confidence": ra.get("confidence", ""),
            f"{b}_confidence": rb.get("confidence", ""),
            f"{a}_parse": ra.get("parse_status", "missing"),
            f"{b}_parse": rb.get("parse_status", "missing"),
            f"{a}_rationale": ra.get("rationale", ""),
            f"{b}_rationale": rb.get("rationale", ""),
        })
    with csv_path.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    # ---- agreement metrics
    verdict_pairs = [(r[f"{a}_verdict"], r[f"{b}_verdict"]) for r in rows]
    binary_pairs = [(r[f"{a}_binary"], r[f"{b}_binary"]) for r in rows]
    k_verdict = common.cohen_kappa(verdict_pairs)
    k_binary = common.cohen_kappa(binary_pairs)
    conf = common.confusion_matrix(verdict_pairs, common.VERDICTS)

    parse_a = Counter(r[f"{a}_parse"] for r in rows)
    parse_b = Counter(r[f"{b}_parse"] for r in rows)
    dist_a = Counter(r[f"{a}_verdict"] for r in rows if r[f"{a}_verdict"])
    dist_b = Counter(r[f"{b}_verdict"] for r in rows if r[f"{b}_verdict"])

    disagreements = [r for r in rows if r[f"{a}_verdict"] and r[f"{b}_verdict"]
                     and r[f"{a}_verdict"] != r[f"{b}_verdict"]]

    def fk(x):
        return "n/a" if x != x else f"{x:.3f}"  # NaN check

    # ---- markdown report
    md = []
    md.append(f"# Test-Patch Audit — Inter-Coder Agreement ({a} vs {b})\n")
    md.append(f"Date: {date} · Index: `{index_path.name}` · Tasks: {len(tasks)}\n")
    md.append(f"- {a}: `{index['agents'][a]['model']}`")
    md.append(f"- {b}: `{index['agents'][b]['model']}`\n")

    md.append("## Headline agreement\n")
    md.append(md_table(
        ["Label", "n scored", "% agreement", "Cohen's κ"],
        [
            ["4-way verdict", str(k_verdict["n"]),
             fk(k_verdict["percent_agreement"]), fk(k_verdict["kappa"])],
            ["binary (witness vs not)", str(k_binary["n"]),
             fk(k_binary["percent_agreement"]), fk(k_binary["kappa"])],
        ],
    ))
    md.append("")

    md.append("## Parse status (verdict recovered from: ok=VERDICT.json, json_repaired=JSON in log, verdict_line='VERDICT:' line)\n")
    md.append(md_table(
        ["Agent", "ok", "json_repaired", "verdict_line", "missing", "total"],
        [
            [a, str(parse_a["ok"]), str(parse_a["json_repaired"]),
             str(parse_a["verdict_line"]), str(parse_a["missing"]), str(sum(parse_a.values()))],
            [b, str(parse_b["ok"]), str(parse_b["json_repaired"]),
             str(parse_b["verdict_line"]), str(parse_b["missing"]), str(sum(parse_b.values()))],
        ],
    ))
    md.append("")

    md.append("## Verdict distribution\n")
    md.append(md_table(
        ["Verdict", a, b],
        [[v, str(dist_a.get(v, 0)), str(dist_b.get(v, 0))] for v in common.VERDICTS]
        + [["(unparsed/empty)",
            str(sum(1 for r in rows if not r[f"{a}_verdict"])),
            str(sum(1 for r in rows if not r[f"{b}_verdict"]))]],
    ))
    md.append("")

    md.append(f"## Confusion matrix (rows = {a}, cols = {b})\n")
    cm_labels = list(conf.keys())
    md.append(md_table(
        [f"{a} \\ {b}"] + cm_labels,
        [[ra] + [str(conf[ra][cb]) for cb in cm_labels] for ra in cm_labels],
    ))
    md.append("")

    md.append(f"## Disagreements ({len(disagreements)})\n")
    if disagreements:
        md.append(md_table(
            ["task", f"{a}", f"{b}", f"{a} rationale", f"{b} rationale"],
            [[r["task"], r[f"{a}_verdict"], r[f"{b}_verdict"],
              (r[f"{a}_rationale"][:160].replace("|", "\\|").replace("\n", " ")),
              (r[f"{b}_rationale"][:160].replace("|", "\\|").replace("\n", " "))]
             for r in disagreements],
        ))
    else:
        md.append("_None._")
    md.append("")
    md.append(f"Full per-task labels: `{csv_path.relative_to(REPO_ROOT)}`\n")

    md_path.write_text("\n".join(md))

    # ---- console summary
    print(f"tasks={len(tasks)}  {a}_parse={dict(parse_a)}  {b}_parse={dict(parse_b)}")
    print(f"verdict: n={k_verdict['n']} %agree={fk(k_verdict['percent_agreement'])} "
          f"kappa={fk(k_verdict['kappa'])}")
    print(f"binary : n={k_binary['n']} %agree={fk(k_binary['percent_agreement'])} "
          f"kappa={fk(k_binary['kappa'])}")
    print(f"disagreements={len(disagreements)}")
    print(f"wrote {csv_path}")
    print(f"wrote {md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
