#!/usr/bin/env python3
"""Self-healing harvest + resume for the trajectory-annotation runs.

The host suspends overnight, killing the screen runs mid-way. This script makes recovery
idempotent:
  1. HARVEST — for each annotator, scan every `jobs/trajannot-<agent>-*/<key>/artifacts/
     annotation.json` (all run tags), newest-wins, validate (real label, not placeholder),
     and copy into the canonical job dir as `annotation__<agent>.json`.
  2. RESUME — for any annotator not yet at full eligible coverage AND with no live
     `run_annotation.py --agents <agent>` process, relaunch it in a detached screen with a
     fresh timestamped tag. run_annotation skips trials whose `annotation__<agent>.json`
     already exists, so it only runs the remainder.

    python3 scripts/traj_analysis/harvest_and_resume.py            # harvest + report only
    python3 scripts/traj_analysis/harvest_and_resume.py --resume   # also relaunch if dead
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
SCREEN = {"codex": "annot_gpt", "opencode": "annot_gemini"}


def harvest(agent: str, trials: list[dict]) -> int:
    out = f"annotation__{agent}.json"
    # newest-wins across all run tags
    best: dict[str, tuple[float, dict]] = {}
    for src in REPO_ROOT.glob(f"jobs/trajannot-{agent}-*/*/artifacts/{common.OUTPUT_FILENAME}"):
        key = src.parent.parent.name
        obj = common._try_json_file(src)
        if obj is None:
            continue
        lab = str((obj.get("leakage") or {}).get("label") or "")
        if not lab or "|" in lab:  # placeholder/garbage -> leave for re-run
            continue
        mtime = src.stat().st_mtime
        if key not in best or mtime > best[key][0]:
            best[key] = (mtime, obj)
    by_key = {t["key"]: t for t in trials}
    wrote = 0
    for key, (_, obj) in best.items():
        t = by_key.get(key)
        if not t:
            continue
        (t["trial_dir"] / out).write_text(json.dumps(obj, indent=2) + "\n")
        wrote += 1
    return wrote


def live(agent: str) -> bool:
    r = subprocess.run(["pgrep", "-af", "run_annotation.py"], capture_output=True, text=True)
    return f"--agents {agent}" in r.stdout


def relaunch(agent: str) -> str:
    tag = f"auto_{agent}_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    log = REPO_ROOT / "jobs" / f"trajannot_{agent}_{tag}.log"
    cmd = (f"python3 scripts/traj_analysis/run_annotation.py --agents {agent} "
           f"--concurrency 4 --tag {tag} > {log} 2>&1")
    subprocess.run(["screen", "-dmS", SCREEN[agent], "bash", "-c", cmd], cwd=REPO_ROOT, check=True)
    return tag


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--resume", action="store_true")
    args = ap.parse_args()
    trials = [t for t in R.discover_trials(["harbor_jobs/v4_withtest219*"]) if t["meta"]["has_trajectory"]]
    n = len(trials)
    for agent in AGENTS:
        done = harvest(agent, trials)
        is_live = live(agent)
        status = f"{agent}: {done}/{n} harvested · live={is_live}"
        if args.resume and done < n and not is_live:
            tag = relaunch(agent)
            status += f" · RELAUNCHED tag={tag} (to-run≈{n - done})"
        elif done >= n:
            status += " · COMPLETE"
        print(status)
    # clean any stray repo-root pollution from opencode
    stray = REPO_ROOT / "annotation.json"
    if stray.exists():
        stray.unlink()
        print("cleaned stray repo-root annotation.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
