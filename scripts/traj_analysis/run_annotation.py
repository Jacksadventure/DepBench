"""Driver: run two labelling agents (independent annotators) over coding-agent
trajectories with harbor_lite, following the annotation protocol. Each (annotator, trial)
produces one annotation.json, which is copied directly into the trial's job directory.

Tasks:        harbor_benchmark/tasks_v4/<owner__repo__PR>/{instruction.md, solution/code.patch}
Trajectories: harbor_jobs/v4_withtest219*/<trial>/{agent/trajectory.json, result.json}

Trials with no agent/trajectory.json are SKIPPED.

Run from the repo root, e.g.:
    # validate discovery only (no agents, no auth needed)
    python3 scripts/traj_analysis/run_annotation.py --dry-run

    # smoke: one job, a few trials, one annotator
    python3 scripts/traj_analysis/run_annotation.py \
        --jobs-glob 'harbor_jobs/v4_withtest219__codex__gpt55*' --limit 3 --agents codex

    # full: two annotators across all v4_withtest219* jobs
    python3 scripts/traj_analysis/run_annotation.py --agents codex,opencode --concurrency 8
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from harbor_lite import (  # noqa: E402
    AgentRuntime,
    ClaudeAgent,
    CodexAgent,
    GeminiAgent,
    OpenCodeAgent,
    RunSpec,
    WorkspaceSpec,
    run_many,
)
from harbor_lite.runs import _slug  # noqa: E402

import common  # noqa: E402

# label -> (constructor, default model). Override the model with `name=model` in --agents.
AGENT_FACTORY = {
    "codex": (CodexAgent, "gpt-5.3-codex"),
    "opencode": (OpenCodeAgent, "github-copilot/gemini-3.1-pro-preview"),
    "claude": (ClaudeAgent, "claude-opus-4-8"),
    "gemini": (GeminiAgent, "pro"),
}


def parse_agents(spec: str) -> list[tuple[str, str]]:
    """'codex,claude=claude-opus-4-8' -> [('codex', <default>), ('claude', 'claude-opus-4-8')]."""
    out: list[tuple[str, str]] = []
    for item in spec.split(","):
        item = item.strip()
        if not item:
            continue
        label, _, model = item.partition("=")
        label = label.strip()
        if label not in AGENT_FACTORY:
            raise SystemExit(f"unknown agent {label!r}; choose from {list(AGENT_FACTORY)}")
        out.append((label, model.strip() or AGENT_FACTORY[label][1]))
    return out


def make_agent(label: str, model: str, env: dict[str, str] | None = None,
               extra_args: tuple[str, ...] = ()):
    ctor, _ = AGENT_FACTORY[label]
    kwargs: dict = {"model": model}
    if env:
        kwargs["env"] = env
    if extra_args:
        kwargs["extra_args"] = extra_args
    return ctor(**kwargs)


def codex_provider_retry_args() -> tuple[str, ...]:
    """Codex sends ~400-500k-token annotation requests; long streams occasionally drop
    ('stream disconnected before completion'). Bump the active provider's stream/request
    retries. Provider name is read from ~/.codex/config.toml so this stays portable.
    """
    cfg = Path.home() / ".codex" / "config.toml"
    if not cfg.exists():
        return ()
    m = re.search(r'(?m)^\s*model_provider\s*=\s*"([^"]+)"', cfg.read_text(errors="replace"))
    if not m:
        return ()
    p = m.group(1)
    return (
        "-c", f"model_providers.{p}.stream_max_retries=5",
        "-c", f"model_providers.{p}.request_max_retries=5",
    )


def make_opencode_env(state_root: Path, key: str) -> dict[str, str]:
    """Per-trial isolated opencode XDG dirs seeded with the Copilot oauth credential.

    opencode shares session state under ~/.local/share/opencode; with concurrency it
    cross-talks. Unique XDG_* dirs per trial isolate that. (Same reasoning as
    scripts/test_patch_agreement/run_audit.py.)
    """
    base = state_root / key
    data, cfg, state, cache = base / "data", base / "config", base / "state", base / "cache"
    for d in (data, cfg, state, cache):
        d.mkdir(parents=True, exist_ok=True)
    src = Path.home() / ".local" / "share" / "opencode" / "auth.json"
    if src.exists():
        dst = data / "opencode" / "auth.json"
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    return {
        "XDG_DATA_HOME": str(data),
        "XDG_CONFIG_HOME": str(cfg),
        "XDG_STATE_HOME": str(state),
        "XDG_CACHE_HOME": str(cache),
    }


def discover_trials(jobs_globs: list[str]) -> list[dict]:
    """Return per-trial dicts (meta + job/trial dirs) for every trial dir found."""
    trials: list[dict] = []
    seen: set[str] = set()
    for pattern in jobs_globs:
        for job_dir in sorted(REPO_ROOT.glob(pattern)):
            if not job_dir.is_dir():
                continue
            for trial_dir in sorted(p for p in job_dir.iterdir() if p.is_dir()):
                if not (trial_dir / "result.json").exists() and not (trial_dir / "agent").exists():
                    continue  # not a trial dir
                key = f"{job_dir.name}__{trial_dir.name}"
                if key in seen:
                    continue
                seen.add(key)
                meta = common.read_trial_meta(trial_dir)
                trials.append(
                    {
                        "key": key,
                        "job": job_dir.name,
                        "job_dir": job_dir,
                        "trial_dir": trial_dir,
                        "meta": meta,
                    }
                )
    return trials


LOCAL_TASKS_DIR = REPO_ROOT / "harbor_benchmark" / "tasks_v4"


def resolve_task_path(meta: dict) -> Path | None:
    """Locate the task dir holding instruction.md + solution/code.patch.

    `result.json`'s `task_id.path` may be absolute and FOREIGN (e.g. the opencode/gemini
    rerun was produced on another machine, recording `/Data2/.../tasks_v4/<name>`). Fall back
    to the local `harbor_benchmark/tasks_v4/<task>` by name, which is what actually exists here.
    """
    candidates: list[Path] = []
    task_dir = meta.get("task_dir")
    if task_dir:
        p = Path(task_dir)
        candidates.append(p if p.is_absolute() else REPO_ROOT / task_dir)
    task = meta.get("task")
    if task:
        candidates.append(LOCAL_TASKS_DIR / task)
    for c in candidates:
        if (c / "instruction.md").exists() and (c / "solution" / "code.patch").exists():
            return c
    return None


def stage_inputs(rec: dict, dest: Path) -> str | None:
    """Stage {instruction.md, oracle.patch, trajectory.json, meta.json, verifier_log.txt?}
    OUTSIDE the repo, git-init'd so agents (esp. opencode) anchor to the stage dir, not the
    DepBench repo. The verifier log is staged ONLY when the trial directory has one.

    Returns a skip reason string, or None on success.
    """
    meta = rec["meta"]
    if not meta["has_trajectory"]:
        return "no trajectory"
    task_path = resolve_task_path(meta)
    if task_path is None:
        return "task inputs (instruction.md + oracle) not found"
    instruction = task_path / "instruction.md"
    oracle = task_path / "solution" / "code.patch"

    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True, exist_ok=True)
    shutil.copy2(instruction, dest / "instruction.md")
    shutil.copy2(oracle, dest / "oracle.patch")
    shutil.copy2(Path(meta["trajectory_path"]), dest / "trajectory.json")

    # Optional held-out test stdout — present only for some runs (e.g. opencode/gemini).
    has_verifier_log = False
    trial_dir = rec.get("trial_dir")
    if trial_dir:
        vlog = Path(trial_dir) / "verifier" / "test-stdout.txt"
        if vlog.exists() and vlog.stat().st_size > 0:
            shutil.copy2(vlog, dest / "verifier_log.txt")
            has_verifier_log = True

    (dest / "meta.json").write_text(
        json.dumps(
            {
                "trial": meta["trial"],
                "task": meta["task"],
                "harness": meta["harness"],
                "llm": meta["model"],
                "model": meta["model"],
                "reward": meta["reward"],
                "exception_type": meta["exception_type"],
                "has_verifier_log": has_verifier_log,
            },
            indent=2,
        )
        + "\n"
    )
    (dest / common.OUTPUT_FILENAME).unlink(missing_ok=True)
    subprocess.run(["git", "init", "-q"], cwd=dest, check=True)
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs-glob", default="harbor_jobs/v4_withtest219*",
                    help="glob(s) for job dirs, comma-separated (relative to repo root)")
    ap.add_argument("--agents", default="codex,opencode",
                    help="comma-separated annotators, each 'name' or 'name=model'")
    ap.add_argument("--limit", type=int, default=None, help="first N eligible trials only")
    ap.add_argument("--job", default=None, help="restrict to one job dir name (substring/glob)")
    ap.add_argument("--trial", default=None, help="restrict to one trial name (smoke)")
    ap.add_argument("--concurrency", type=int, default=4)
    ap.add_argument("--timeout", type=float, default=1200.0)
    ap.add_argument("--jobs-dir", default="jobs")
    ap.add_argument("--stage-root", default=None,
                    help="where to stage isolated inputs; MUST be outside the repo "
                         "(default: ~/.cache/depbench_trajannot_stage)")
    ap.add_argument("--out-prefix", default="annotation",
                    help="job-dir output filename prefix -> <prefix>__<agent>.json")
    ap.add_argument("--overwrite", action="store_true",
                    help="re-annotate trials whose job-dir output already exists")
    ap.add_argument("--protocol", default=None, help="override protocol markdown path")
    ap.add_argument("--no-oc-isolate", action="store_true")
    ap.add_argument("--dry-run", action="store_true",
                    help="discover + report the plan; do not stage or run agents")
    ap.add_argument("--tag", default=None)
    args = ap.parse_args()

    tag = args.tag or datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    jobs_dir = (REPO_ROOT / args.jobs_dir).resolve()
    globs = [g.strip() for g in args.jobs_glob.split(",") if g.strip()]
    annotators = parse_agents(args.agents)

    stage_root_base = (
        Path(args.stage_root).expanduser().resolve()
        if args.stage_root
        else Path.home() / ".cache" / "depbench_trajannot_stage"
    )
    if REPO_ROOT in stage_root_base.parents or stage_root_base == REPO_ROOT:
        ap.error(f"--stage-root must be OUTSIDE the repo ({REPO_ROOT}); got {stage_root_base}")

    all_trials = discover_trials(globs)
    if args.job:
        all_trials = [t for t in all_trials if args.job in t["job"]]
    if args.trial:
        all_trials = [t for t in all_trials if args.trial in t["trial_dir"].name]

    eligible = [t for t in all_trials if t["meta"]["has_trajectory"]]
    skipped_no_traj = [t for t in all_trials if not t["meta"]["has_trajectory"]]
    if args.limit:
        eligible = eligible[: args.limit]

    print(f"discovered: {len(all_trials)} trials  | eligible (have traj): {len(eligible)}  "
          f"| skipped (no traj): {len(skipped_no_traj)}", flush=True)
    rewards = {"pass": 0, "fail": 0, "no_reward": 0}
    for t in eligible:
        r = t["meta"]["reward"]
        rewards["pass" if r == 1.0 else "fail" if r == 0.0 else "no_reward"] += 1
    print(f"eligible rewards: {rewards}", flush=True)

    protocol_path = Path(args.protocol).resolve() if args.protocol else None
    prompt = common.build_prompt(common.load_protocol_text(protocol_path))

    stage_root = stage_root_base / tag
    oc_state_root = stage_root / "_ocstate"
    runtime = AgentRuntime(disable_web=True, isolated_state=False, timeout_sec=args.timeout)

    index: dict = {
        "tag": tag,
        "jobs_globs": globs,
        "annotators": {},
        "trials": {label: {} for label, _ in annotators},
        "skipped_no_trajectory": [t["key"] for t in skipped_no_traj],
    }

    for label, model in annotators:
        job_name = f"trajannot-{label}-{tag}"
        out_name = f"{args.out_prefix}__{label}.json"
        specs = []
        planned = done = staged_skips = 0
        for t in eligible:
            job_out_path = t["trial_dir"] / out_name
            index["trials"][label][t["key"]] = {
                "job": t["job"],
                "task": t["meta"]["task"],
                "reward": t["meta"]["reward"],
                "job_trial_dir": str(t["trial_dir"]),
                "job_out_path": str(job_out_path),
                "harbor_trial_dir": str(jobs_dir / job_name / _slug(t["key"])),
                "stage_dir": str(stage_root / label / t["key"]),
                "agent_output_name": AGENT_FACTORY[label][0].output_name,
            }
            if job_out_path.exists() and not args.overwrite:
                done += 1
                continue
            if args.dry_run:
                planned += 1
                continue
            stage_dir = stage_root / label / t["key"]
            skip = stage_inputs(t, stage_dir)
            if skip:
                staged_skips += 1
                index["trials"][label][t["key"]]["skip_reason"] = skip
                continue
            env = None
            if label == "opencode" and not args.no_oc_isolate:
                env = make_opencode_env(oc_state_root, t["key"])
            extra = codex_provider_retry_args() if label == "codex" else ()
            specs.append(
                RunSpec(
                    name=t["key"],
                    agent=make_agent(label, model, env, extra),
                    prompt=prompt,
                    workspace=WorkspaceSpec.existing(stage_dir, clean=False),
                    runtime=runtime,
                    artifact_paths=(common.OUTPUT_FILENAME,),
                    metadata={"key": t["key"], "task": t["meta"]["task"],
                              "annotator": label, "model": model},
                )
            )
            planned += 1

        index["annotators"][label] = {
            "model": model,
            "out_name": out_name,
            "harbor_job_dir": str(jobs_dir / job_name),
            "agent_output_name": AGENT_FACTORY[label][0].output_name,
        }

        print(f"\n=== annotator={label} model={model}  to-run={len(specs)} "
              f"already-done={done} staged-skips={staged_skips} (dry_run={args.dry_run}) ===",
              flush=True)
        if args.dry_run or not specs:
            continue

        run_many(
            specs,
            concurrency=args.concurrency,
            jobs_dir=str(jobs_dir),
            workspace_root=str(jobs_dir / "_ws" / tag),
            job_name=job_name,
        )

        # Copy each validated annotation directly into its harbor_jobs trial directory.
        written = 0
        for t in eligible:
            info = index["trials"][label][t["key"]]
            rec = common.load_annotation(
                meta=t["meta"],
                job_out_path=Path(info["job_out_path"]),
                trial_dir=Path(info["harbor_trial_dir"]),
                stage_dir=Path(info["stage_dir"]),
                agent_output_name=info["agent_output_name"],
            )
            info["parse_status"] = rec["parse_status"]
            if rec["parse_status"] in ("ok", "json_repaired") and rec.get("raw"):
                Path(info["job_out_path"]).write_text(
                    json.dumps(rec["raw"], indent=2) + "\n"
                )
                written += 1
        print(f"annotator={label}: wrote {written} annotation files into job dirs", flush=True)

    index_path = jobs_dir / f"trajannot-index-{tag}.json"
    jobs_dir.mkdir(parents=True, exist_ok=True)
    index_path.write_text(json.dumps(index, indent=2) + "\n")
    print(f"\nwrote index -> {index_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
