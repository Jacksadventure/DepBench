#!/usr/bin/env python3
"""Dump the trajectory of one (task, llm, harness) trial from the v4_withtest219 exports.

Usage: python3 extract_trial.py <task> <llm> <harness> [outfile]
  llm in {gpt55, claude48, gemini35flash}; harness in {codex, copilot_cli, opencode, claude_code}
Writes pretty-printed trajectory JSON (or raw text) to outfile (default: ./trials/<task>__<llm>__<harness>.json)
"""
import gzip, json, os, sys

EXPORT = "/fast/hrz/DepBench/harbor_benchmark/trajectory_exports/v4_withtest219_20260627"

def main():
    task, llm, harness = sys.argv[1:4]
    out = sys.argv[4] if len(sys.argv) > 4 else None
    path = os.path.join(EXPORT, f"{llm}__{harness}.jsonl.gz")
    with gzip.open(path, "rt") as f:
        for line in f:
            rec = json.loads(line)
            if rec["task"] != task:
                continue
            if out is None:
                os.makedirs("trials", exist_ok=True)
                out = f"trials/{task}__{llm}__{harness}.json"
            traj = rec.get("trajectory")
            with open(out, "w") as o:
                meta = {k: v for k, v in rec.items() if k != "trajectory"}
                o.write(json.dumps(meta, indent=1))
                o.write("\n\n===== TRAJECTORY =====\n")
                if isinstance(traj, str):
                    try:
                        traj = json.loads(traj)
                    except json.JSONDecodeError:
                        pass
                o.write(traj if isinstance(traj, str) else json.dumps(traj, indent=1))
            print(f"wrote {out} (reward={rec.get('reward')}, exception={rec.get('exception_type') or 'none'})")
            return
    sys.exit(f"not found: {task} in {path}")

if __name__ == "__main__":
    main()
