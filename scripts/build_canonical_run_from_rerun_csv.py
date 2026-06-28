#!/usr/bin/env python3
"""Materialize a canonical ``harbor_jobs/<job>/`` run directory from a rerun-results CSV.

Background
----------
The canonical per-(harness, llm) directories under ``harbor_jobs/v4_withtest219__*`` are
local, *gitignored* viewer conveniences. For most harnesses they were reconstructed from
the trajectory-export JSONL archives. The opencode/gemini-3.5-flash export was effectively
empty (the original run failed), so its canonical dir held 219 placeholder trials with
truncated names and no trajectories.

The opencode/gemini rerun (``opencode_gemini35flash_v4_withtest_219_fixed_conc5_setup1200_*``
plus its ``resume14`` follow-up) produced real Harbor trials *with verifier logs*. The
coauthor's rerun-results CSV is the authoritative per-task merge: each row pins, for one of
the 219 tasks, the exact ``trial`` directory inside a ``source_job`` (segment ``base205of219``
or ``resume14``) that should populate the canonical ``job``.

This script copies each pinned source trial directory (full Harbor trial: ``agent/``,
``verifier/``, ``artifacts/``, ``config.json``, ``result.json``, ``trial.log``) into the
canonical job dir, and removes any stale trial dirs that are not in the CSV. It is
idempotent. The output lives under gitignored ``harbor_jobs/`` and is not committed.

Usage
-----
    python3 scripts/build_canonical_run_from_rerun_csv.py            # dry-run (default)
    python3 scripts/build_canonical_run_from_rerun_csv.py --apply
"""
from __future__ import annotations

import argparse
import csv
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
HARBOR_JOBS = REPO_ROOT / "harbor_jobs"
DEFAULT_CSV = (
    REPO_ROOT
    / "harbor_benchmark/reports/v4_with_test219_opencode_gemini_rerun_results_2026-06-28.csv"
)


def load_rows(csv_path: Path) -> list[dict[str, str]]:
    with csv_path.open(newline="") as fh:
        rows = list(csv.DictReader(fh))
    required = {"task", "trial", "job", "source_job"}
    missing = required - set(rows[0].keys()) if rows else required
    if missing:
        sys.exit(f"CSV {csv_path} missing required columns: {sorted(missing)}")
    return rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default=str(DEFAULT_CSV), help="rerun-results CSV (authoritative merge)")
    ap.add_argument("--apply", action="store_true", help="perform the copy (default: dry-run)")
    args = ap.parse_args()

    csv_path = Path(args.csv).resolve()
    rows = load_rows(csv_path)

    job_names = {r["job"] for r in rows}
    if len(job_names) != 1:
        sys.exit(f"CSV references multiple canonical jobs, refusing: {sorted(job_names)}")
    canonical = HARBOR_JOBS / job_names.pop()

    # Validate every pinned source trial exists before touching anything.
    plan: list[tuple[Path, Path, dict[str, str]]] = []
    errors: list[str] = []
    for r in rows:
        src = HARBOR_JOBS / r["source_job"] / r["trial"]
        dst = canonical / r["trial"]
        if not src.is_dir():
            errors.append(f"missing source trial: {src}")
        plan.append((src, dst, r))
    if errors:
        print("\n".join(errors), file=sys.stderr)
        sys.exit(f"{len(errors)} source trials missing; aborting (no changes made)")

    csv_trials = {r["trial"] for r in rows}
    stale = (
        [p for p in canonical.iterdir() if p.is_dir() and p.name not in csv_trials]
        if canonical.exists()
        else []
    )

    have_traj = sum(1 for s, _, _ in plan if (s / "agent" / "trajectory.json").exists())
    have_verifier = sum(1 for s, _, _ in plan if (s / "verifier").is_dir())
    print(f"canonical dir : {canonical}")
    print(f"CSV           : {csv_path.relative_to(REPO_ROOT)}")
    print(f"pinned trials : {len(plan)}  (with trajectory: {have_traj}, with verifier/: {have_verifier})")
    print(f"stale dirs to remove: {len(stale)}")
    if not args.apply:
        print("\nDRY-RUN — re-run with --apply to perform the copy.")
        return 0

    for p in stale:
        shutil.rmtree(p)
    copied = 0
    for src, dst, _ in plan:
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
        copied += 1
    print(f"\nremoved {len(stale)} stale trial dirs; copied {copied} trials into {canonical.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
