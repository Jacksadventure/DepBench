from __future__ import annotations

import os
import signal
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

from ..runtime import AgentRuntime
from .utils import fallback_answer


@dataclass(frozen=True)
class AgentResult:
    agent: str
    model: str | None
    command: tuple[str, ...]
    exit_code: int
    started_at: float
    finished_at: float
    log_path: Path
    state_dir: Path | None


class LocalAgent:
    """Base class for a local non-interactive coding-agent CLI."""

    name = "agent"
    runner = "agent"
    executable = "agent"
    output_name = "agent.txt"
    default_model: str | None = None

    def __init__(
        self,
        *,
        model: str | None = None,
        extra_args: Sequence[str] = (),
        env: Mapping[str, str] | None = None,
    ) -> None:
        self.model = model or self.default_model
        self.extra_args = tuple(extra_args)
        self.env = dict(env or {})

    def build_command(self, prompt: str, runtime: AgentRuntime) -> list[str]:
        raise NotImplementedError

    def disable_web_args(self) -> Sequence[str]:
        return ()

    def session_files(self, *, workdir: Path, state_dir: Path | None, started_at: float) -> Sequence[Path]:
        return ()

    def trajectory_sources(self, *, raw_log_path: Path, sessions_dir: Path) -> Sequence[Path]:
        return (raw_log_path,)

    def build_trajectory_steps(
        self,
        events: Sequence[dict[str, Any]],
        *,
        fallback_timestamp: str,
    ) -> list[dict[str, Any]]:
        return []

    def extract_trajectory_answer(self, events: Sequence[dict[str, Any]], raw_text: str) -> str | None:
        return fallback_answer(raw_text)

    def extract_trajectory_stats(self, events: Sequence[dict[str, Any]]) -> dict[str, Any]:
        return {}

    def state_env(self, state_dir: Path) -> dict[str, str]:
        return {"HOME": str(state_dir / "home")}

    def runtime_env(self, *, workdir: Path, state_dir: Path | None, runtime: AgentRuntime) -> dict[str, str]:
        env = os.environ.copy()
        env.update(self.env)
        env.update(runtime.env)
        if runtime.isolated_state and state_dir is not None:
            home = state_dir / "home"
            home.mkdir(parents=True, exist_ok=True)
            env.update(self.state_env(state_dir))
        return env

    def combined_args(self, runtime: AgentRuntime) -> list[str]:
        args: list[str] = []
        if runtime.disable_web:
            args.extend(self.disable_web_args())
        args.extend(self.extra_args)
        args.extend(runtime.extra_args)
        return args

    def run(
        self,
        *,
        prompt: str,
        workdir: Path,
        artifact_dir: Path,
        runtime: AgentRuntime | None = None,
    ) -> AgentResult:
        runtime = runtime or AgentRuntime()
        artifact_dir.mkdir(parents=True, exist_ok=True)
        state_dir = runtime.state_dir or artifact_dir.parent / "state" / self.name
        if runtime.isolated_state:
            state_dir.mkdir(parents=True, exist_ok=True)
        log_path = artifact_dir / self.output_name

        # Expose the prepared workdir so agents (e.g. opencode) can pin themselves to it
        # instead of walking up to the outer repo's git root.
        self.workdir = workdir
        command = self.build_command(prompt, runtime)
        env = self.runtime_env(workdir=workdir, state_dir=state_dir, runtime=runtime)

        started = time.time()
        with log_path.open("w", encoding="utf-8", errors="replace") as log:
            log.write("$ " + " ".join(command) + "\n\n")
            log.flush()
            proc = subprocess.Popen(
                command,
                cwd=workdir,
                env=env,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )
            try:
                assert proc.stdout is not None
                deadline = None if runtime.timeout_sec is None else started + runtime.timeout_sec
                for line in proc.stdout:
                    log.write(line)
                    log.flush()
                    if runtime.stream_to_stdout:
                        print(line, end="")
                    if deadline is not None and time.time() > deadline:
                        proc.send_signal(signal.SIGTERM)
                        try:
                            proc.wait(timeout=10)
                        except subprocess.TimeoutExpired:
                            proc.kill()
                        break
                exit_code = proc.wait(timeout=5)
            except BaseException:
                proc.kill()
                raise

        return AgentResult(
            agent=self.name,
            model=self.model,
            command=tuple(command),
            exit_code=exit_code,
            started_at=started,
            finished_at=time.time(),
            log_path=log_path,
            state_dir=state_dir if runtime.isolated_state else None,
        )

    @staticmethod
    def _recent_files(roots: Sequence[Path], patterns: Sequence[str], started_at: float) -> list[Path]:
        out: list[Path] = []
        seen: set[Path] = set()
        for root in roots:
            if not root.exists():
                continue
            for pattern in patterns:
                for path in root.glob(pattern):
                    try:
                        resolved = path.resolve()
                        if resolved in seen or not path.is_file():
                            continue
                        if path.stat().st_mtime >= started_at - 5:
                            out.append(path)
                            seen.add(resolved)
                    except OSError:
                        continue
        return sorted(out, key=lambda p: p.stat().st_mtime)

    @staticmethod
    def _state_home(state_dir: Path | None) -> Path | None:
        return None if state_dir is None else state_dir / "home"
