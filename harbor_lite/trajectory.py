from __future__ import annotations

import json
import shutil
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence

from .agents import LocalAgent


@dataclass(frozen=True)
class TrajectoryCollector:
    """Collect raw sessions and write a best-effort trajectory file."""

    agent: LocalAgent

    def collect(
        self,
        *,
        workdir: Path,
        raw_log_path: Path,
        agent_dir: Path,
        started_at: float,
        finished_at: float | None = None,
        prompt: str | None = None,
        status: str = "completed",
        exit_code: int | None = None,
        state_dir: Path | None = None,
    ) -> Path | None:
        agent_dir.mkdir(parents=True, exist_ok=True)
        copied_log = agent_dir / raw_log_path.name
        if raw_log_path.exists() and raw_log_path.resolve() != copied_log.resolve():
            shutil.copy2(raw_log_path, copied_log)

        self._copy_sessions(
            workdir=workdir,
            agent_dir=agent_dir,
            started_at=started_at,
            state_dir=state_dir,
        )
        trajectory_path = agent_dir / "trajectory.json"
        self._write_atif_trajectory(
            trajectory_path,
            raw_log_path=raw_log_path,
            agent_dir=agent_dir,
            started_at=started_at,
            finished_at=finished_at,
            prompt=prompt,
            status=status,
            exit_code=exit_code,
        )
        return trajectory_path

    def _copy_sessions(
        self,
        *,
        workdir: Path,
        agent_dir: Path,
        started_at: float,
        state_dir: Path | None,
    ) -> None:
        sessions_dir = agent_dir / "sessions"
        for src in self.agent.session_files(workdir=workdir, state_dir=state_dir, started_at=started_at):
            if not src.is_file():
                continue
            sessions_dir.mkdir(parents=True, exist_ok=True)
            dst = self._session_destination(sessions_dir, src)
            shutil.copy2(src, dst)

    @staticmethod
    def _session_destination(sessions_dir: Path, src: Path) -> Path:
        dst = sessions_dir / src.name
        if not dst.exists():
            return dst
        stem = src.stem
        suffix = src.suffix
        index = 2
        while True:
            candidate = sessions_dir / f"{stem}.{index}{suffix}"
            if not candidate.exists():
                return candidate
            index += 1

    def _write_atif_trajectory(
        self,
        path: Path,
        *,
        raw_log_path: Path,
        agent_dir: Path,
        started_at: float,
        finished_at: float | None,
        prompt: str | None,
        status: str,
        exit_code: int | None,
    ) -> None:
        text = raw_log_path.read_text(errors="replace") if raw_log_path.exists() else ""
        fallback_timestamp = _iso(started_at)
        events = self._read_events(
            self.agent.trajectory_sources(raw_log_path=raw_log_path, sessions_dir=agent_dir / "sessions")
        )
        runner_steps = self.agent.build_trajectory_steps(events, fallback_timestamp=fallback_timestamp)
        answer = self.agent.extract_trajectory_answer(events, text)
        stats = self.agent.extract_trajectory_stats(events)

        steps: list[dict[str, Any]] = []
        if prompt:
            steps.append(
                {
                    "step_id": 1,
                    "timestamp": fallback_timestamp,
                    "source": "user",
                    "message": prompt,
                }
            )
        steps.extend(runner_steps)
        finished_timestamp = _iso(finished_at or time.time())
        if status == "completed":
            steps.append(
                {
                    "step_id": 1,
                    "timestamp": finished_timestamp,
                    "source": "agent",
                    "model_name": self.agent.model,
                    "message": answer or "(no assistant answer captured)",
                    "llm_call_count": 1,
                    "extra": {"kind": "final_answer"},
                }
            )
        else:
            message = f"harbor_lite run {status}"
            if exit_code is not None:
                message += f": agent exited with code {exit_code}"
            steps.append(
                {
                    "step_id": 1,
                    "timestamp": finished_timestamp,
                    "source": "agent",
                    "model_name": self.agent.model,
                    "message": message,
                    "observation": {
                        "results": [
                            {
                                "content": text[-20000:] or message,
                                "extra": {"status": status, "exit_code": exit_code},
                            }
                        ]
                    },
                    "llm_call_count": 0,
                    "extra": {"kind": "error", "status": status, "exit_code": exit_code},
                }
            )

        steps = [{**step, "step_id": index} for index, step in enumerate(_clean(steps), start=1)]
        payload = {
            "schema_version": "ATIF-v1.7",
            "session_id": path.parent.parent.name,
            "trajectory_id": path.parent.parent.name,
            "agent": {
                "name": self.agent.name,
                "version": "harbor_lite",
                "model_name": self.agent.model,
                "extra": {"runner": self.agent.runner},
            },
            "steps": steps,
            "final_metrics": _final_metrics(stats, len(steps)),
            "notes": "Experimental ATIF trajectory exported by harbor_lite.",
            "extra": {
                "status": status,
                "runner": self.agent.runner,
                "raw_log": raw_log_path.name,
                "event_count": len(events),
                "generated_at": _iso(time.time()),
            },
        }
        path.write_text(json.dumps(payload, indent=2) + "\n")

    @staticmethod
    def _read_events(paths: Sequence[Path]) -> list[dict[str, Any]]:
        events: list[dict[str, Any]] = []
        seen: set[Path] = set()
        for path in paths:
            try:
                resolved = path.resolve()
            except OSError:
                continue
            if resolved in seen or not path.exists():
                continue
            seen.add(resolved)
            for line in path.read_text(errors="replace").splitlines():
                line = line.strip()
                if not line or not line.startswith("{"):
                    continue
                try:
                    event = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if isinstance(event, dict):
                    events.append(event)
        return events


def _iso(value: float) -> str:
    return datetime.fromtimestamp(value, tz=timezone.utc).isoformat().replace("+00:00", "Z")


def _clean(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _clean(val) for key, val in value.items() if val is not None and val != {} and val != []}
    if isinstance(value, list):
        return [_clean(item) for item in value if item is not None]
    return value


def _number(value: object) -> int | float | None:
    return value if isinstance(value, (int, float)) else None


def _final_metrics(stats: dict[str, Any], total_steps: int) -> dict[str, Any]:
    prompt = _number(
        stats.get("prompt_tokens")
        or stats.get("input_tokens")
        or stats.get("input")
        or _nested(stats, ("tokens", "input"))
    )
    completion = _number(
        stats.get("completion_tokens")
        or stats.get("output_tokens")
        or stats.get("output")
        or _nested(stats, ("tokens", "output"))
    )
    cached = _number(
        stats.get("cached_tokens")
        or stats.get("cached_input_tokens")
        or stats.get("cache_read_tokens")
        or _nested(stats, ("tokens", "cached"))
        or _nested(stats, ("cache", "read"))
    )
    cost = _number(stats.get("cost_usd") or stats.get("total_cost_usd") or stats.get("cost"))
    extra = {"raw_stats": stats} if stats else None
    return _clean(
        {
            "total_prompt_tokens": int(prompt) if prompt is not None else None,
            "total_completion_tokens": int(completion) if completion is not None else None,
            "total_cached_tokens": int(cached) if cached is not None else None,
            "total_cost_usd": float(cost) if cost is not None else None,
            "total_steps": total_steps,
            "extra": extra,
        }
    )


def _nested(root: dict[str, Any], segments: Sequence[str]) -> object:
    current: object = root
    for segment in segments:
        if not isinstance(current, dict):
            return None
        current = current.get(segment)
    return current
