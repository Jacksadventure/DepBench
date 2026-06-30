#!/usr/bin/env python3
"""Finalize the trajectory-annotation study: when BOTH annotators are complete (1170/1170),
export the raw annotations to a tracked path (harbor_jobs/ is gitignored), regenerate the
report, and commit + push to GitHub. Idempotent and safe to run repeatedly from cron:
it no-ops until complete, pushes once, then a sentinel prevents re-pushing.

    python3 scripts/traj_analysis/finalize_and_push.py            # act only if complete
    python3 scripts/traj_analysis/finalize_and_push.py --status   # just print coverage
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
DEST = REPO_ROOT / "harbor_benchmark" / "annotations" / "v4_withtest219_20260630"
SENTINEL = DEST / ".pushed"
BRANCH = "v4-with-test"


def coverage(trials):
    out = {}
    for a in AGENTS:
        out[a] = sum(1 for t in trials if (t["trial_dir"] / f"annotation__{a}.json").exists())
    return out


def export_jsonl(agent: str, trials: list[dict]) -> int:
    """One row per annotated trial: key/task/harness/llm/reward + the raw annotation object."""
    DEST.mkdir(parents=True, exist_ok=True)
    rows = []
    for t in sorted(trials, key=lambda x: x["key"]):
        p = t["trial_dir"] / f"annotation__{agent}.json"
        obj = common._try_json_file(p)
        if obj is None:
            continue
        m = t["meta"]
        rows.append({
            "key": t["key"], "task": m["task"], "harness": m.get("harness"),
            "llm": m.get("model"), "reward": m.get("reward"), "annotation": obj,
        })
    (DEST / f"{agent}.jsonl").write_text("".join(json.dumps(r, sort_keys=True) + "\n" for r in rows))
    return len(rows)


def git(*args, check=True):
    return subprocess.run(["git", *args], cwd=REPO_ROOT, text=True,
                          capture_output=True, check=check)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--status", action="store_true")
    args = ap.parse_args()

    trials = [t for t in R.discover_trials(["harbor_jobs/v4_withtest219*"]) if t["meta"]["has_trajectory"]]
    n = len(trials)
    cov = coverage(trials)
    print(f"coverage: " + ", ".join(f"{a}={cov[a]}/{n}" for a in AGENTS))

    if args.status:
        return 0
    if SENTINEL.exists():
        print("already finalized + pushed (sentinel present); nothing to do.")
        return 0
    if any(cov[a] < n for a in AGENTS):
        print("not complete yet — no export/push.")
        return 0

    # --- complete: export raw annotations + regenerate report
    for a in AGENTS:
        c = export_jsonl(a, trials)
        print(f"exported {a}.jsonl ({c} rows)")
    (DEST / "index.json").write_text(json.dumps({
        "dataset": "v4-with-test219", "eligible_trials": n, "annotators": AGENTS,
        "coverage": cov, "files": [f"{a}.jsonl" for a in AGENTS],
    }, indent=2) + "\n")
    subprocess.run(["python3", "scripts/traj_analysis/report.py"], cwd=REPO_ROOT, check=True)
    report = REPO_ROOT / "harbor_benchmark" / "reports" / \
        f"traj_annotation_report_{datetime.now(timezone.utc).strftime('%Y-%m-%d')}.md"

    # --- commit + push (explicit paths only; autostash protects the dirty worktree)
    paths = [str(DEST.relative_to(REPO_ROOT)),
             str(report.relative_to(REPO_ROOT)),
             "scripts/traj_analysis"]
    git("add", *paths)
    status = git("status", "--porcelain", *paths).stdout.strip()
    if status:
        git("commit", "-m",
            "Add final trajectory-annotation results + report\n\n"
            "Raw per-trial annotations (codex + opencode) and the regenerated leakage report.\n\n"
            "Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>")
        pull = git("pull", "--rebase", "--autostash", "origin", BRANCH, check=False)
        print(pull.stdout[-400:], pull.stderr[-400:])
        push = git("push", "origin", BRANCH, check=False)
        print(push.stdout[-400:] or push.stderr[-400:])
        if push.returncode == 0:
            SENTINEL.write_text(datetime.now(timezone.utc).isoformat() + "\n")
            print("PUSHED final results. You can delete the recurring cron jobs now.")
        else:
            print("PUSH FAILED — left commit local; will retry next tick.")
    else:
        print("nothing new to commit.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
