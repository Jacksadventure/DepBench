"""Build a Harbor-loadable job directory from a finished oracle-miner run.

Uses Harbor's own agent classes to parse trajectories and Harbor's
Pydantic models to write ``config.json`` / ``result.json`` so the
output can be browsed by ``harbor view <jobs_dir>``.

Layout produced:

    <jobs_dir>/<job_id>/
        config.json            (JobConfig)
        result.json            (JobResult)
        <trial_name>/
            config.json        (TrialConfig)
            result.json        (TrialResult)
            agent/
                trajectory.json
                <agent>.txt    (raw stdout, mirrors harbor)
                sessions/      (codex/claude only — copied from agent's data dir)
            artifacts/
                instruction.md
                cheatsheet.md
                opencode.log   (raw mixed log including --print-logs)
                manifest.json
"""
from __future__ import annotations

import json
import logging
import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from harbor.agents.installed.opencode import OpenCode
from harbor.agents.installed.codex import Codex
from harbor.agents.installed.claude_code import ClaudeCode
from harbor.agents.installed.gemini_cli import GeminiCli
from harbor.models.job.config import (
    DatasetConfig,
    JobConfig,
    RetryConfig,
)
from harbor.models.job.result import JobResult, JobStats
from harbor.models.task.id import LocalTaskId
from harbor.models.trajectories.trajectory import Trajectory
from harbor.models.trial.config import (
    AgentConfig,
    EnvironmentConfig,
    TaskConfig,
    TrialConfig,
    VerifierConfig,
)
from harbor.models.trial.result import AgentInfo, ModelInfo, TrialResult
from harbor.utils.trajectory_utils import format_trajectory_json


_AGENT_ALIASES = {
    "opencode": OpenCode,
    "codex": Codex,
    "claude": ClaudeCode,
    "gemini": GeminiCli,
    "qwen": GeminiCli,
}
_OUTPUT_NAME = {
    "opencode": "opencode.txt",
    "codex": "codex.txt",
    "claude": "claude-code.txt",
    "gemini": "gemini-cli.txt",
    "qwen": "qwen-code.txt",
}


def _instantiate_agent(agent: str, *, logs_dir: Path, model_name: str | None):
    """Construct a Harbor agent shell suitable for trajectory parsing.

    We never call ``run()`` — only the trajectory-conversion methods.
    Most ``__init__`` arguments are therefore irrelevant but Harbor
    enforces them, so we pass empty placeholders.
    """
    cls = _AGENT_ALIASES[agent]
    common: dict[str, Any] = {
        "logs_dir": logs_dir,
        "model_name": model_name,
        "logger": logging.getLogger(f"oracle-miner.{agent}"),
    }
    if agent == "opencode":
        return cls(**common)
    if agent == "codex":
        return cls(version=None, extra_env=None, **common)
    if agent == "claude":
        return cls(memory_dir=None, **common)
    if agent in ("gemini", "qwen"):
        return cls(**common)
    raise ValueError(f"Unsupported agent: {agent!r}")


def _find_codex_session_files(worktree: Path, started_at: datetime) -> list[Path]:
    """Locate codex session JSONL files for this specific worktree.

    Codex stores per-session JSONL under ``$CODEX_HOME/sessions`` (default
    ``~/.codex/sessions``). Each file contains a ``session_meta`` record
    whose payload includes the run ``cwd``. We use that to select only the
    files belonging to the current worktree, then fall back to a coarse
    timestamp filter if the metadata is absent.
    """
    import os
    candidates = [
        Path(os.environ.get("CODEX_HOME", "~/.codex")).expanduser() / "sessions",
        Path("~/.codex/sessions").expanduser(),
    ]
    for root in candidates:
        if not root.exists():
            continue
        matched: list[Path] = []
        fallback: list[Path] = []
        for jsonl in sorted(root.rglob("*.jsonl"), key=lambda p: p.stat().st_mtime):
            if jsonl.stat().st_mtime < started_at.timestamp() - 5:
                continue
            fallback.append(jsonl)
            try:
                with jsonl.open() as handle:
                    for line in handle:
                        stripped = line.strip()
                        if not stripped:
                            continue
                        event = json.loads(stripped)
                        if event.get("type") != "session_meta":
                            continue
                        payload = event.get("payload", {})
                        cwd = payload.get("cwd")
                        if isinstance(cwd, str) and Path(cwd).resolve() == worktree.resolve():
                            matched.append(jsonl)
                        break
            except (OSError, json.JSONDecodeError):
                continue
        if matched:
            return matched
        if fallback:
            return fallback
    return []


def _find_claude_session_dir(worktree: Path) -> Path | None:
    """Locate the claude-code session JSONL directory for this worktree.

    Claude Code stores sessions under
    ``~/.claude/projects/<encoded-cwd>/`` where ``<encoded-cwd>`` is the
    absolute worktree path with ``/`` replaced by ``-``.
    """
    base = Path("~/.claude/projects").expanduser()
    if not base.exists():
        return None
    encoded = str(worktree.resolve()).replace("/", "-")
    candidate = base / encoded
    if candidate.exists():
        return candidate
    # Fallback: most recent project dir
    children = [c for c in base.iterdir() if c.is_dir()]
    if not children:
        return None
    return max(children, key=lambda p: p.stat().st_mtime)


def _find_gemini_session_file(started_at: datetime) -> Path | None:
    """Locate the Gemini CLI session file written during this run.

    Gemini CLI stores chats under ``~/.gemini/tmp/**/session-*.jsonl`` (or
    legacy ``.json``). The file format embeds a project hash but not the
    plain cwd, so for local oracle-miner runs we select the newest session
    file created near the run start time.
    """
    base = Path("~/.gemini/tmp").expanduser()
    if not base.exists():
        return None
    candidates = sorted(
        (
            p for p in base.rglob("session-*")
            if p.suffix in {".jsonl", ".json"}
        ),
        key=lambda p: p.stat().st_mtime,
    )
    if not candidates:
        return None
    recent = [p for p in candidates if p.stat().st_mtime >= started_at.timestamp() - 5]
    if recent:
        return recent[-1]
    return candidates[-1]


def _find_qwen_session_file(started_at: datetime) -> Path | None:
    """Locate the Qwen CLI session file written during this run.

    Qwen Code stores chats under ``~/.qwen/projects/<project>/chats/<uuid>.jsonl``.
    """
    base = Path("~/.qwen/projects").expanduser()
    if not base.exists():
        return None
    candidates = sorted(
        (p for p in base.rglob("chats/*.jsonl")),
        key=lambda p: p.stat().st_mtime,
    )
    if not candidates:
        return None
    recent = [p for p in candidates if p.stat().st_mtime >= started_at.timestamp() - 5]
    if recent:
        return recent[-1]
    return candidates[-1]


def parse_trajectory(
    agent: str,
    *,
    agent_dir: Path,
    raw_log_path: Path,
    model_name: str | None,
    worktree: Path,
    started_at: datetime,
) -> Trajectory | None:
    """Stage stdout + sessions inside ``agent_dir`` and convert to ATIF.

    Returns the Harbor ``Trajectory`` object (or ``None`` if conversion
    yielded no steps). The caller is responsible for serialising it.
    """
    agent_dir.mkdir(parents=True, exist_ok=True)
    handler = _instantiate_agent(agent, logs_dir=agent_dir, model_name=model_name)

    if agent == "opencode":
        # Harbor expects logs_dir/opencode.txt; copy our raw log there.
        shutil.copy2(raw_log_path, agent_dir / OpenCode._OUTPUT_FILENAME)
        events = handler._parse_stdout()
        return handler._convert_events_to_trajectory(events)

    if agent == "codex":
        # Copy the raw stdout (kept alongside as codex.txt for symmetry).
        shutil.copy2(raw_log_path, agent_dir / Codex._OUTPUT_FILENAME)
        session_files = _find_codex_session_files(worktree, started_at)
        sessions_dst = agent_dir / "sessions"
        sessions_dst.mkdir(exist_ok=True)
        for jsonl in session_files:
            shutil.copy2(jsonl, sessions_dst / jsonl.name)
        return handler._convert_events_to_trajectory(sessions_dst)

    if agent == "claude":
        shutil.copy2(raw_log_path, agent_dir / "claude-code.txt")
        sessions_src = _find_claude_session_dir(worktree)
        sessions_dst = agent_dir / "sessions" / "projects"
        sessions_dst.mkdir(parents=True, exist_ok=True)
        if sessions_src is not None and sessions_src.exists():
            target = sessions_dst / sessions_src.name
            if target.exists():
                shutil.rmtree(target)
            shutil.copytree(sessions_src, target)
        return handler._convert_events_to_trajectory(agent_dir / "sessions")

    if agent == "gemini":
        shutil.copy2(raw_log_path, agent_dir / "gemini-cli.txt")
        gemini_src = _find_gemini_session_file(started_at)
        if gemini_src is None:
            return None
        gemini_dst = agent_dir / f"gemini-cli.trajectory.{gemini_src.suffix.lstrip('.')}"
        shutil.copy2(gemini_src, gemini_dst)
        gemini_trajectory = handler._load_gemini_session(gemini_dst)
        if gemini_trajectory is None:
            return None
        return handler._convert_gemini_to_atif(gemini_trajectory)

    if agent == "qwen":
        shutil.copy2(raw_log_path, agent_dir / "qwen-code.txt")
        qwen_src = _find_qwen_session_file(started_at)
        if qwen_src is None:
            return None
        qwen_dst = agent_dir / f"qwen-cli.trajectory.{qwen_src.suffix.lstrip('.')}"
        shutil.copy2(qwen_src, qwen_dst)
        qwen_trajectory = handler._load_gemini_session(qwen_dst)
        if qwen_trajectory is None:
            return None
        return handler._convert_gemini_to_atif(qwen_trajectory)

    raise ValueError(f"Unsupported agent: {agent!r}")


def _model_info(model_name: str | None) -> ModelInfo | None:
    if not model_name:
        return None
    fields = ModelInfo.model_fields
    payload: dict[str, Any] = {}
    if "name" in fields:
        payload["name"] = model_name
    if "model_name" in fields:
        payload["model_name"] = model_name
    try:
        return ModelInfo(**payload)
    except Exception:
        return None


def write_harbor_job(
    jobs_dir: Path,
    *,
    job_id: str,
    trial_name: str,
    instance_id: str,
    repo: str,
    base_commit: str,
    agent: str,
    agent_version: str,
    model_name: str | None,
    started_at: datetime,
    finished_at: datetime,
    trajectory: Trajectory | None,
    raw_log_path: Path,
    artifact_paths: dict[str, Path],
    exit_code: int | None,
    worktree: Path,
) -> Path:
    """Write a Harbor-shaped job to ``jobs_dir/<job_id>/``.

    Note: harbor's existing jobs use naive ISO timestamps; mixing aware
    and naive ``started_at`` values crashes ``harbor view`` when it sorts
    job summaries. We strip ``tzinfo`` (assuming UTC) to stay consistent.
    """
    if started_at.tzinfo is not None:
        started_at = started_at.astimezone(timezone.utc).replace(tzinfo=None)
    if finished_at.tzinfo is not None:
        finished_at = finished_at.astimezone(timezone.utc).replace(tzinfo=None)
    jobs_dir = Path(jobs_dir)
    job_root = jobs_dir / job_id
    trial_root = job_root / trial_name
    agent_dir = trial_root / "agent"
    artifacts_dir = trial_root / "artifacts"
    agent_dir.mkdir(parents=True, exist_ok=True)
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    # ── trajectory.json (already built by parse_trajectory caller) ──
    if trajectory is not None:
        (agent_dir / "trajectory.json").write_text(
            format_trajectory_json(trajectory.to_json_dict())
        )

    # ── artifacts ──
    for name, src in artifact_paths.items():
        if src is not None and Path(src).exists():
            shutil.copy2(src, artifacts_dir / name)

    # ``manifest.json`` is consumed by harbor's viewer frontend, which
    # expects a list of ``{source, destination, type}`` entries (see
    # ``ArtifactManifestEntry`` in apps/viewer/app/lib/types.ts). We list
    # each copied artifact; the ``source`` column points back to where it
    # came from on disk so the viewer can render provenance.
    manifest_entries = [
        {
            "source": str(Path(src).resolve()) if src else name,
            "destination": name,
            "type": "directory" if Path(src).is_dir() else "file",
        }
        for name, src in artifact_paths.items()
        if src is not None and Path(src).exists()
    ]
    (artifacts_dir / "manifest.json").write_text(
        json.dumps(manifest_entries, indent=2) + "\n"
    )

    # Run metadata that is *not* part of the harbor-defined manifest goes
    # to a sibling file so it is still visible in the viewer's file list.
    meta = {
        "instance_id": instance_id,
        "repo": repo,
        "base_commit": base_commit,
        "agent": agent,
        "agent_version": agent_version,
        "model": model_name,
        "started_at": started_at.isoformat(),
        "finished_at": finished_at.isoformat(),
        "exit_code": exit_code,
        "worktree": str(worktree),
    }
    (artifacts_dir / "oracle-miner-meta.json").write_text(
        json.dumps(meta, indent=2) + "\n"
    )

    # ── trial config.json (TrialConfig) ──
    trial_config = TrialConfig(
        trial_name=trial_name,
        task=TaskConfig(name=instance_id, source=f"swe-bench-verified:{instance_id}"),
        agent=AgentConfig(name=agent, model_name=model_name),
        environment=EnvironmentConfig(),
        verifier=VerifierConfig(disable=True),
        artifacts=[],
    )
    (trial_root / "config.json").write_text(
        trial_config.model_dump_json(indent=2) + "\n"
    )

    # ── trial result.json (TrialResult) ──
    trial_uuid = uuid.uuid4()
    trial_result = TrialResult(
        id=trial_uuid,
        task_name=instance_id,
        trial_name=trial_name,
        trial_uri=str(trial_root.resolve()),
        task_id=LocalTaskId(path=worktree.resolve()),
        task_checksum="sha256:" + base_commit,
        config=trial_config,
        agent_info=AgentInfo(
            name=agent,
            version=agent_version,
            model_info=_model_info(model_name),
        ),
        started_at=started_at,
        finished_at=finished_at,
    )
    (trial_root / "result.json").write_text(
        trial_result.model_dump_json(indent=2) + "\n"
    )

    # ── job config.json (JobConfig) ──
    job_config = JobConfig(
        job_name=job_id,
        jobs_dir=jobs_dir,
        retry=RetryConfig(),
        environment=EnvironmentConfig(),
        verifier=VerifierConfig(disable=True),
        metrics=[],
        agents=[AgentConfig(name=agent, model_name=model_name)],
        datasets=[
            DatasetConfig(name="swe-bench-verified", source="huggingface"),
        ] if "name" in DatasetConfig.model_fields else [],
        tasks=[TaskConfig(name=instance_id)],
        artifacts=[],
    )
    (job_root / "config.json").write_text(
        job_config.model_dump_json(indent=2) + "\n"
    )

    # ── job result.json (JobResult) ──
    succeeded = 1 if (exit_code == 0 and trajectory is not None) else 0
    job_result = JobResult(
        id=uuid.uuid4(),
        started_at=started_at,
        finished_at=finished_at,
        n_total_trials=1,
        stats=JobStats(
            n_completed_trials=succeeded,
            n_errored_trials=1 - succeeded,
        ),
        trial_results=[trial_result],
    )
    (job_root / "result.json").write_text(
        job_result.model_dump_json(indent=2) + "\n"
    )

    return job_root


def utcnow() -> datetime:
    return datetime.now(timezone.utc)
