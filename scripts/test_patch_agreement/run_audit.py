"""Driver: run codex + opencode as independent static auditors over tasks_v4.

Each (agent, task) gets an isolated staged copy of the task dir; the agent reads the
patches and writes VERDICT.json, collected via harbor_lite artifact_paths.

Run from the repo root, e.g.:
    python3 scripts/test_patch_agreement/run_audit.py --task actix__actix__554 --agents opencode   # smoke
    python3 scripts/test_patch_agreement/run_audit.py --agents codex,opencode                      # full
"""
from __future__ import annotations

import argparse
import json
import os
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
    CodexAgent,
    OpenCodeAgent,
    RunSpec,
    WorkspaceSpec,
    run_many,
)
from harbor_lite.runs import _slug  # noqa: E402

import common  # noqa: E402

AGENT_FACTORY = {
    "codex": lambda: CodexAgent(model="gpt-5.3-codex"),
    "opencode": lambda: OpenCodeAgent(model="github-copilot/gemini-3.1-pro-preview"),
}


def list_tasks(tasks_root: Path) -> list[str]:
    return sorted(p.name for p in tasks_root.iterdir() if p.is_dir())


def stage_task(tasks_root: Path, task: str, dest: Path) -> Path:
    """Stage an isolated copy and make it a standalone git repo.

    Agents (notably opencode) resolve their project root by walking up to the nearest
    .git. If the stage dir lived inside the DepBench tree, the agent would anchor to the
    repo root and read/write the real dataset. So stage OUTSIDE the repo AND `git init`
    each copy, guaranteeing the agent's project root is the staged dir.
    """
    if dest.exists():
        shutil.rmtree(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(tasks_root / task, dest, symlinks=True)
    # never let a stale verdict survive into a fresh run
    (dest / "VERDICT.json").unlink(missing_ok=True)
    subprocess.run(["git", "init", "-q"], cwd=dest, check=True)
    return dest


def make_opencode_env(state_root: Path, task: str) -> dict[str, str]:
    """Per-trial isolated opencode XDG dirs, seeded with the Copilot oauth credential.

    opencode keeps a shared session/server store under ~/.local/share/opencode; with
    isolated_state=False, concurrent `opencode run` processes cross-talk (one trial's
    agent ends up analyzing another's files). Giving each trial unique XDG_* dirs
    isolates that state. We copy auth.json into the per-trial data dir so Copilot oauth
    still resolves.
    """
    base = state_root / task
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


def build_agent(agent_name: str, task: str, oc_state_root: Path, isolate_oc: bool):
    if agent_name == "opencode" and isolate_oc:
        env = make_opencode_env(oc_state_root, task)
        return OpenCodeAgent(model="github-copilot/gemini-3.1-pro-preview", env=env)
    return AGENT_FACTORY[agent_name]()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tasks-root", default="harbor_benchmark/tasks_v4")
    ap.add_argument("--agents", default="codex,opencode")
    ap.add_argument("--task", default=None, help="single task name (smoke)")
    ap.add_argument("--tasks-file", default=None,
                    help="newline-separated task names to restrict the run (e.g. re-run misses)")
    ap.add_argument("--limit", type=int, default=None, help="first N tasks only")
    ap.add_argument("--concurrency", type=int, default=4)
    ap.add_argument("--timeout", type=float, default=900.0)
    ap.add_argument("--jobs-dir", default="jobs")
    ap.add_argument("--stage-root", default=None,
                    help="where to stage isolated task copies; MUST be outside the repo "
                         "(default: ~/.cache/depbench_agreement_stage)")
    ap.add_argument("--no-oc-isolate", action="store_true",
                    help="disable per-trial opencode XDG isolation (NOT recommended for concurrency>1)")
    ap.add_argument("--tag", default=None, help="run tag (default: UTC timestamp)")
    args = ap.parse_args()

    tasks_root = (REPO_ROOT / args.tasks_root).resolve()
    jobs_dir = (REPO_ROOT / args.jobs_dir).resolve()
    tag = args.tag or datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    stage_root_base = (
        Path(args.stage_root).expanduser().resolve()
        if args.stage_root
        else Path.home() / ".cache" / "depbench_agreement_stage"
    )
    if REPO_ROOT in stage_root_base.parents or stage_root_base == REPO_ROOT:
        ap.error(f"--stage-root must be OUTSIDE the repo ({REPO_ROOT}); got {stage_root_base}")
    agents = [a.strip() for a in args.agents.split(",") if a.strip()]
    for a in agents:
        if a not in AGENT_FACTORY:
            ap.error(f"unknown agent {a!r}; choose from {list(AGENT_FACTORY)}")

    if args.task:
        tasks = [args.task]
    elif args.tasks_file:
        raw = Path(args.tasks_file).read_text().splitlines()
        tasks = [t.strip() for t in raw if t.strip()]
    else:
        tasks = list_tasks(tasks_root)
        if args.limit:
            tasks = tasks[: args.limit]

    stage_root = stage_root_base / tag
    oc_state_root = stage_root / "_ocstate"
    isolate_oc = not args.no_oc_isolate
    runtime = AgentRuntime(disable_web=True, isolated_state=False, timeout_sec=args.timeout)

    index: dict = {
        "tag": tag,
        "tasks_root": str(tasks_root),
        "tasks": tasks,
        "agents": {},
        "trials": {a: {} for a in agents},
    }

    for agent_name in agents:
        job_name = f"agreement-{agent_name}-{tag}"
        agent_obj = AGENT_FACTORY[agent_name]()
        specs = []
        for task in tasks:
            stage_dir = stage_root / agent_name / task
            stage_task(tasks_root, task, stage_dir)
            specs.append(
                RunSpec(
                    name=task,
                    agent=build_agent(agent_name, task, oc_state_root, isolate_oc),
                    prompt=common.AUDIT_PROMPT,
                    workspace=WorkspaceSpec.existing(stage_dir, clean=False),
                    runtime=runtime,
                    artifact_paths=("VERDICT.json",),
                    metadata={"task": task, "agent": agent_name, "model": agent_obj.model},
                )
            )
            index["trials"][agent_name][task] = {
                "trial_dir": str(jobs_dir / job_name / _slug(task)),
                "stage_dir": str(stage_dir),
                "agent_output_name": agent_obj.output_name,
            }
        index["agents"][agent_name] = {
            "job_dir": str(jobs_dir / job_name),
            "model": agent_obj.model,
            "output_name": agent_obj.output_name,
        }
        print(f"\n=== running agent={agent_name} model={agent_obj.model} "
              f"tasks={len(specs)} concurrency={args.concurrency} ===", flush=True)
        run_many(
            specs,
            concurrency=args.concurrency,
            jobs_dir=str(jobs_dir),
            workspace_root=str(jobs_dir / "_ws" / tag),
            job_name=job_name,
        )

    index_path = jobs_dir / f"agreement-index-{tag}.json"
    index_path.write_text(json.dumps(index, indent=2) + "\n")
    print(f"\nwrote index -> {index_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
