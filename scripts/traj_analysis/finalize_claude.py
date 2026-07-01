#!/usr/bin/env python3
"""Finalize the CLAUDE-4.8 annotation group: when both annotators reach full coverage over the
four claude48 source runs, export raw annotations to claude48_{codex,opencode}.jsonl, generate a
claude leakage-findings + report, and commit + push. Idempotent; pushes once via a sentinel.

    python3 scripts/traj_analysis/finalize_claude.py            # act only if complete
    python3 scripts/traj_analysis/finalize_claude.py --status   # just print coverage
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import common  # noqa: E402
import run_annotation as R  # noqa: E402

AGENTS = ["codex", "opencode"]
GLOB = ("harbor_jobs/codex_claude48_v4_withtest_219_conc10_2026-06-26__1248-00,"
        "harbor_jobs/copilot_cli_claude48_byok_v4_withtest_219_conc10_2026-06-26__1248-00,"
        "harbor_jobs/opencode_claude48_v4_withtest_219_conc10_2026-06-26__1248-00,"
        "harbor_jobs/claude_code_claude48_v4_withtest_219_conc10_2026-06-26__ready-00")
DEST = REPO_ROOT / "harbor_benchmark" / "annotations" / "v4_withtest219_20260630"
SENTINEL = DEST / ".pushed_claude48"
BRANCH = "v4-with-test"


def trials():
    globs = [g.strip() for g in GLOB.split(",") if g.strip()]
    return [t for t in R.discover_trials(globs) if t["meta"]["has_trajectory"]]


def export(agent, ts):
    rows = []
    for t in sorted(ts, key=lambda x: x["key"]):
        obj = common._try_json_file(t["trial_dir"] / f"annotation__{agent}.json")
        if obj is None:
            continue
        m = t["meta"]
        rows.append({"key": t["key"], "task": m["task"], "harness": m.get("harness"),
                     "llm": m.get("model"), "reward": m.get("reward"), "annotation": obj})
    (DEST / f"claude48_{agent}.jsonl").write_text(
        "".join(json.dumps(r, sort_keys=True) + "\n" for r in rows))
    return len(rows)


def git(*a, check=True):
    return subprocess.run(["git", *a], cwd=REPO_ROOT, text=True, capture_output=True, check=check)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--status", action="store_true")
    args = ap.parse_args()
    ts = trials()
    n = len(ts)
    cov = {a: sum(1 for t in ts if (t["trial_dir"] / f"annotation__{a}.json").exists()) for a in AGENTS}
    print("coverage(claude48): " + ", ".join(f"{a}={cov[a]}/{n}" for a in AGENTS))
    if args.status:
        return 0
    if SENTINEL.exists():
        print("already finalized + pushed (claude48 sentinel present).")
        return 0
    if any(cov[a] < n for a in AGENTS):
        print("not complete yet — no export/push.")
        return 0

    DEST.mkdir(parents=True, exist_ok=True)
    for a in AGENTS:
        print(f"exported claude48_{a}.jsonl ({export(a, ts)} rows)")
    date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    report = f"harbor_benchmark/reports/traj_annotation_report_claude48_{date}.md"
    subprocess.run(["python3", "scripts/traj_analysis/report.py", "--jobs-glob", GLOB,
                    "--out", report], cwd=REPO_ROOT, check=True)
    subprocess.run(["python3", "scripts/traj_analysis/leakage_findings.py", "--jobs-glob", GLOB,
                    "--prefix", "claude48_"], cwd=REPO_ROOT, check=True)

    paths = [f"harbor_benchmark/annotations/v4_withtest219_20260630/claude48_codex.jsonl",
             f"harbor_benchmark/annotations/v4_withtest219_20260630/claude48_opencode.jsonl",
             f"harbor_benchmark/annotations/v4_withtest219_20260630/claude48_leakage_findings.csv",
             f"harbor_benchmark/annotations/v4_withtest219_20260630/claude48_leakage_findings.md",
             report, "scripts/traj_analysis"]
    git("add", *paths)
    if git("status", "--porcelain", *paths).stdout.strip():
        git("commit", "-m",
            "Add Claude-4.8 trajectory annotations + leakage findings\n\n"
            f"Raw per-trial annotations for the claude-4.8 group ({n} trials x 4 harnesses), "
            "codex + opencode annotators, plus leakage findings and report.\n\n"
            "Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>")
        git("pull", "--rebase", "--autostash", "origin", BRANCH, check=False)
        push = git("push", "origin", BRANCH, check=False)
        print((push.stdout or push.stderr)[-300:])
        if push.returncode == 0:
            SENTINEL.write_text(datetime.now(timezone.utc).isoformat() + "\n")
            print("PUSHED claude48 results. You can delete the claude cron jobs now.")
        else:
            print("PUSH FAILED — commit left local; will retry next tick.")
    else:
        print("nothing new to commit.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
