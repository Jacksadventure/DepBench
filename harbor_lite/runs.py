from __future__ import annotations

import inspect
import json
import re
import shutil
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Sequence

from .agents import AgentResult, LocalAgent
from .artifacts import copy_globs, write_exception_tail, write_manifest
from .runtime import AgentRuntime
from .trajectory import TrajectoryCollector
from .workspace import Workspace, WorkspaceSpec


def _slug(value: str) -> str:
    value = re.sub(r"[^A-Za-z0-9_.-]+", "-", value).strip("-")
    return value or "run"


def default_job_name(caller: str | None = None) -> str:
    if caller is None:
        frame = inspect.stack()[1]
        caller = Path(frame.filename).stem
    parts = [p for p in re.split(r"[-_.]+", Path(caller).stem) if p]
    suffix = parts[-1] if parts else "run"
    return f"{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H-%M-%SZ')}-{_slug(suffix)}"


@dataclass(frozen=True)
class RunSpec:
    name: str
    agent: LocalAgent
    prompt: str
    workspace: WorkspaceSpec
    runtime: AgentRuntime = field(default_factory=AgentRuntime)
    copied_paths: Sequence[str] = ()
    artifact_paths: Sequence[str] = ()
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class RunResult:
    name: str
    ok: bool
    exit_code: int | None
    job_dir: Path
    trial_dir: Path
    workspace: Path
    log_path: Path
    started_at: datetime
    finished_at: datetime
    trial_result: dict[str, object]


def run_one(
    spec: RunSpec,
    *,
    jobs_dir: Path | str = "jobs",
    workspace_root: Path | str = "workspace",
    job_name: str | None = None,
    keep_workspace: bool = True,
    quiet: bool = False,
    print_final_status: bool = True,
    write_job_files: bool = True,
    job_id: str | None = None,
) -> RunResult:
    job_name = job_name or default_job_name()
    job_id = job_id or str(uuid.uuid4())
    jobs_dir = Path(jobs_dir)
    workspace_root = Path(workspace_root)
    job_dir = jobs_dir / job_name
    trial_name = _slug(spec.name)
    trial_dir = job_dir / trial_name
    artifacts_dir = trial_dir / "artifacts"
    agent_dir = trial_dir / "agent"
    workdir = workspace_root / job_name / trial_name / "repo"

    artifacts_dir.mkdir(parents=True, exist_ok=True)
    agent_dir.mkdir(parents=True, exist_ok=True)
    _write_status(trial_dir, "preparing")
    if not quiet:
        _print_progress(
            spec,
            "preparing",
            f"workspace={workdir} prompt={_one_line(spec.prompt)}",
        )

    workspace = spec.workspace.prepare(workdir)
    if spec.copied_paths:
        copy_globs(spec.copied_paths, src_root=Path.cwd(), dst_root=workspace.path)

    started = datetime.now(timezone.utc)
    _write_status(trial_dir, "running", started_at=started.isoformat())
    if not quiet:
        _print_progress(
            spec,
            "running",
            f"agent={spec.agent.name} model={spec.agent.model or '-'} log={artifacts_dir / spec.agent.output_name}",
        )
    agent_result = spec.agent.run(
        prompt=spec.prompt,
        workdir=workspace.path,
        artifact_dir=artifacts_dir,
        runtime=spec.runtime,
    )
    finished = datetime.now(timezone.utc)

    copied_agent_log = agent_dir / spec.agent.output_name
    shutil.copy2(agent_result.log_path, copied_agent_log)
    TrajectoryCollector(spec.agent).collect(
        workdir=workspace.path,
        raw_log_path=agent_result.log_path,
        agent_dir=agent_dir,
        started_at=agent_result.started_at,
        finished_at=agent_result.finished_at,
        prompt=spec.prompt,
        status="completed" if agent_result.exit_code == 0 else "errored",
        exit_code=agent_result.exit_code,
        state_dir=agent_result.state_dir,
    )

    manifest = copy_globs(spec.artifact_paths, src_root=workspace.path, dst_root=artifacts_dir)
    manifest.append(
        {
            "source": str(agent_result.log_path.resolve()),
            "destination": spec.agent.output_name,
            "type": "file",
        }
    )
    write_manifest(artifacts_dir / "manifest.json", manifest)

    if agent_result.exit_code != 0:
        write_exception_tail(
            trial_dir / "exception.txt",
            log_path=agent_result.log_path,
            exit_code=agent_result.exit_code,
        )

    trial_result = _write_trial_json(
        trial_dir,
        spec=spec,
        workspace=workspace,
        agent_result=agent_result,
        started=started,
        finished=finished,
        job_id=job_id,
    )
    if write_job_files:
        _write_job_files(
            job_dir,
            specs=[spec],
            trial_results=[trial_result],
            job_id=job_id,
            started=started,
            updated=finished,
            finished=finished,
            n_total_trials=1,
            n_concurrent_trials=1,
        )

    status = "completed" if agent_result.exit_code == 0 else "errored"
    _write_status(
        trial_dir,
        status,
        started_at=started.isoformat(),
        finished_at=finished.isoformat(),
        exit_code=agent_result.exit_code,
    )
    if not quiet and print_final_status:
        duration = _format_duration((finished - started).total_seconds())
        if agent_result.exit_code == 0:
            detail = f"duration={duration} artifacts={artifacts_dir}"
        else:
            detail = (
                f"exit_code={agent_result.exit_code} duration={duration} "
                f"exception={trial_dir / 'exception.txt'}"
            )
        _print_progress(spec, status, detail)

    if not keep_workspace and workspace.owned:
        shutil.rmtree(workspace.path, ignore_errors=True)

    return RunResult(
        name=spec.name,
        ok=agent_result.exit_code == 0,
        exit_code=agent_result.exit_code,
        job_dir=job_dir,
        trial_dir=trial_dir,
        workspace=workspace.path,
        log_path=agent_result.log_path,
        started_at=started,
        finished_at=finished,
        trial_result=trial_result,
    )


def run_many(
    specs: Sequence[RunSpec],
    *,
    concurrency: int = 1,
    jobs_dir: Path | str = "jobs",
    workspace_root: Path | str = "workspace",
    job_name: str | None = None,
    keep_workspace: bool = True,
    quiet: bool = False,
) -> list[RunResult]:
    job_name = job_name or default_job_name()
    job_id = str(uuid.uuid4())
    results: list[RunResult] = []
    total = len(specs)
    job_dir = Path(jobs_dir) / job_name
    job_started = datetime.now(timezone.utc)
    _write_job_files(
        job_dir,
        specs=specs,
        trial_results=[],
        job_id=job_id,
        started=job_started,
        updated=job_started,
        finished=None,
        n_total_trials=total,
        n_concurrent_trials=concurrency,
        n_running_trials=min(concurrency, total),
    )
    with ThreadPoolExecutor(max_workers=concurrency) as pool:
        futures = [
            pool.submit(
                run_one,
                spec,
                jobs_dir=jobs_dir,
                workspace_root=workspace_root,
                job_name=job_name,
                keep_workspace=keep_workspace,
                quiet=quiet,
                print_final_status=False,
                write_job_files=False,
                job_id=job_id,
            )
            for spec in specs
        ]
        for fut in as_completed(futures):
            result = fut.result()
            results.append(result)
            if not quiet:
                _print_counted_result(result, done=len(results), total=total)
            _write_summary(job_dir, results, n_total_trials=total)
            remaining = total - len(results)
            _write_job_files(
                job_dir,
                specs=specs,
                trial_results=[r.trial_result for r in results],
                job_id=job_id,
                started=job_started,
                updated=datetime.now(timezone.utc),
                finished=None,
                n_total_trials=total,
                n_concurrent_trials=concurrency,
                n_running_trials=min(concurrency, remaining),
            )
    finished = datetime.now(timezone.utc)
    _write_summary(job_dir, results, n_total_trials=total)
    _write_job_files(
        job_dir,
        specs=specs,
        trial_results=[r.trial_result for r in results],
        job_id=job_id,
        started=job_started,
        updated=finished,
        finished=finished,
        n_total_trials=total,
        n_concurrent_trials=concurrency,
        n_running_trials=0,
    )
    return results


def _one_line(text: str, *, limit: int = 120) -> str:
    line = " ".join(text.split())
    if len(line) <= limit:
        return repr(line)
    return repr(line[: limit - 1] + "…")


def _format_duration(seconds: float) -> str:
    seconds = max(0, int(round(seconds)))
    minutes, sec = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours}h{minutes:02d}m{sec:02d}s"
    if minutes:
        return f"{minutes}m{sec:02d}s"
    return f"{sec}s"


def _print_progress(spec: RunSpec, status: str, detail: str) -> None:
    stamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{stamp}] {spec.name} {status}: {detail}", flush=True)


def _print_counted_result(result: RunResult, *, done: int, total: int) -> None:
    stamp = datetime.now().strftime("%H:%M:%S")
    duration = _format_duration((result.finished_at - result.started_at).total_seconds())
    if result.ok:
        status = "completed"
        detail = f"duration={duration} artifacts={result.trial_dir / 'artifacts'}"
    else:
        status = "errored"
        detail = (
            f"exit_code={result.exit_code} duration={duration} "
            f"exception={result.trial_dir / 'exception.txt'}"
        )
    print(f"[{stamp}] [{done}/{total}] {result.name} {status}: {detail}", flush=True)


def _write_status(trial_dir: Path, status: str, **extra: object) -> None:
    payload = {"status": status, "updated_at": datetime.now(timezone.utc).isoformat(), **extra}
    trial_dir.mkdir(parents=True, exist_ok=True)
    (trial_dir / "status.json").write_text(json.dumps(payload, indent=2) + "\n")


def _write_trial_json(
    trial_dir: Path,
    *,
    spec: RunSpec,
    workspace: Workspace,
    agent_result: AgentResult,
    started: datetime,
    finished: datetime,
    job_id: str,
) -> dict[str, object]:
    task_path = workspace.path.resolve()
    config = {
        "task": {"path": str(task_path), "source": "local"},
        "trial_name": trial_dir.name,
        "trials_dir": str(trial_dir.parent),
        "timeout_multiplier": 1.0,
        "agent_timeout_multiplier": None,
        "verifier_timeout_multiplier": None,
        "agent_setup_timeout_multiplier": None,
        "environment_build_timeout_multiplier": None,
        "agent": {"name": spec.agent.name, "model_name": spec.agent.model},
        "environment": {"kwargs": {"runner": "harbor_lite", "mode": "local"}},
        "verifier": {"disable": True},
        "artifacts": list(spec.artifact_paths),
        "extra_instruction_paths": [],
        "job_id": job_id,
    }
    agent_context = {
        "n_input_tokens": None,
        "n_cache_tokens": None,
        "n_output_tokens": None,
        "cost_usd": None,
        "rollout_details": None,
        "metadata": {
            "command": list(agent_result.command),
            "log_path": str(agent_result.log_path),
            "runner": "harbor_lite",
            **spec.metadata,
        },
    }
    result = {
        "id": str(uuid.uuid4()),
        "task_name": spec.name,
        "trial_name": trial_dir.name,
        "trial_uri": trial_dir.resolve().as_uri(),
        "task_id": {"path": str(task_path)},
        "source": "local",
        "task_checksum": workspace.base_commit or f"local:{task_path}",
        "config": config,
        "agent_info": {
            "name": spec.agent.name,
            "version": "unknown",
            "model_info": _model_info(spec.agent.model),
        },
        "agent_result": agent_context,
        "verifier_result": None,
        "started_at": started.isoformat(),
        "finished_at": finished.isoformat(),
        "environment_setup": None,
        "agent_setup": None,
        "agent_execution": {
            "started_at": started.isoformat(),
            "finished_at": finished.isoformat(),
        },
        "verifier": None,
        "step_results": None,
        "exception_info": None
        if agent_result.exit_code == 0
        else {
            "exception_type": "AgentExitError",
            "exception_message": f"agent exited with code {agent_result.exit_code}",
            "exception_traceback": "",
            "occurred_at": finished.isoformat(),
        },
    }
    (trial_dir / "config.json").write_text(json.dumps(config, indent=2) + "\n")
    (trial_dir / "result.json").write_text(json.dumps(result, indent=2) + "\n")
    return result


def _write_job_files(
    job_dir: Path,
    *,
    specs: Sequence[RunSpec],
    trial_results: Sequence[dict[str, object]],
    job_id: str,
    started: datetime,
    updated: datetime,
    finished: datetime | None,
    n_total_trials: int,
    n_concurrent_trials: int,
    n_running_trials: int = 0,
) -> None:
    job_dir.mkdir(parents=True, exist_ok=True)
    agents = []
    seen_agents: set[tuple[str, str | None]] = set()
    for spec in specs:
        key = (spec.agent.name, spec.agent.model)
        if key in seen_agents:
            continue
        seen_agents.add(key)
        agents.append({"name": spec.agent.name, "model_name": spec.agent.model})
    config = {
        "job_name": job_dir.name,
        "jobs_dir": str(job_dir.parent),
        "n_attempts": 1,
        "timeout_multiplier": 1.0,
        "agent_timeout_multiplier": None,
        "verifier_timeout_multiplier": None,
        "agent_setup_timeout_multiplier": None,
        "environment_build_timeout_multiplier": None,
        "debug": False,
        "n_concurrent_trials": n_concurrent_trials,
        "quiet": False,
        "retry": {
            "max_retries": 0,
            "include_exceptions": None,
            "exclude_exceptions": [
                "AgentTimeoutError",
                "VerifierTimeoutError",
                "RewardFileNotFoundError",
                "RewardFileEmptyError",
                "VerifierOutputParseError",
            ],
            "wait_multiplier": 1.0,
            "min_wait_sec": 1.0,
            "max_wait_sec": 60.0,
        },
        "environment": {"kwargs": {"runner": "harbor_lite", "mode": "local"}},
        "verifier": {"disable": True},
        "metrics": [],
        "agents": agents,
        "datasets": [],
        "tasks": _job_tasks(specs, trial_results, job_dir),
        "artifacts": sorted({path for spec in specs for path in spec.artifact_paths}),
        "extra_instruction_paths": [],
        "plugins": [],
    }
    completed = len(trial_results)
    errored = sum(1 for result in trial_results if result.get("exception_info") is not None)
    stats = {
        "n_completed_trials": completed,
        "n_errored_trials": errored,
        "n_running_trials": n_running_trials,
        "n_pending_trials": max(n_total_trials - completed - n_running_trials, 0),
        "n_cancelled_trials": 0,
        "n_retries": 0,
        "evals": _eval_stats(trial_results),
        "n_input_tokens": None,
        "n_cache_tokens": None,
        "n_output_tokens": None,
        "cost_usd": None,
    }
    result = {
        "id": job_id,
        "started_at": started.isoformat(),
        "updated_at": updated.isoformat(),
        "finished_at": finished.isoformat() if finished else None,
        "n_total_trials": 1,
        "stats": stats,
        "trial_results": list(trial_results),
    }
    result["n_total_trials"] = n_total_trials
    (job_dir / "config.json").write_text(json.dumps(config, indent=2) + "\n")
    (job_dir / "result.json").write_text(json.dumps(result, indent=2) + "\n")


def _write_summary(
    job_dir: Path,
    results: Sequence[RunResult],
    *,
    n_total_trials: int | None = None,
) -> None:
    job_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "job": job_dir.name,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "total": n_total_trials if n_total_trials is not None else len(results),
        "completed": sum(1 for r in results if r.ok),
        "errored": sum(1 for r in results if not r.ok),
        "results": [
            {
                "name": r.name,
                "ok": r.ok,
                "exit_code": r.exit_code,
                "trial_dir": str(r.trial_dir),
                "workspace": str(r.workspace),
            }
            for r in results
        ],
    }
    (job_dir / "summary.json").write_text(json.dumps(payload, indent=2) + "\n")


def _model_info(model: str | None) -> dict[str, str | None] | None:
    if not model:
        return None
    if "/" in model:
        provider, name = model.split("/", 1)
        return {"name": name, "provider": provider}
    return {"name": model, "provider": None}


def _job_tasks(
    specs: Sequence[RunSpec],
    trial_results: Sequence[dict[str, object]],
    job_dir: Path,
) -> list[dict[str, str]]:
    tasks: list[dict[str, str]] = []
    seen: set[str] = set()
    for result in trial_results:
        config = result.get("config")
        if not isinstance(config, dict):
            continue
        task = config.get("task")
        if not isinstance(task, dict):
            continue
        path = task.get("path")
        if isinstance(path, str) and path not in seen:
            seen.add(path)
            tasks.append({"path": path, "source": str(task.get("source") or "local")})
    for spec in specs:
        fallback = str((job_dir / spec.name).resolve())
        if fallback not in seen:
            seen.add(fallback)
            tasks.append({"path": fallback, "source": "local"})
    return tasks


def _eval_stats(trial_results: Sequence[dict[str, object]]) -> dict[str, dict[str, object]]:
    stats: dict[str, dict[str, object]] = {}
    for result in trial_results:
        agent_info = result.get("agent_info")
        if not isinstance(agent_info, dict):
            continue
        agent_name = str(agent_info.get("name") or "unknown")
        model_info = agent_info.get("model_info")
        model_name = None
        if isinstance(model_info, dict):
            model_name = model_info.get("name")
        source = str(result.get("source") or "adhoc")
        key = f"{agent_name}__{model_name}__{source}" if model_name else f"{agent_name}__{source}"
        entry = stats.setdefault(
            key,
            {
                "n_trials": 0,
                "n_errors": 0,
                "metrics": [],
                "pass_at_k": {},
                "reward_stats": {},
                "exception_stats": {},
            },
        )
        exception = result.get("exception_info")
        if isinstance(exception, dict):
            entry["n_errors"] = int(entry["n_errors"]) + 1
            exception_type = str(exception.get("exception_type") or "Exception")
            exception_stats = entry["exception_stats"]
            assert isinstance(exception_stats, dict)
            exception_stats.setdefault(exception_type, []).append(result.get("trial_name"))
    return stats
