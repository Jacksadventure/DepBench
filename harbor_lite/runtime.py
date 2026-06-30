from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Mapping, Sequence


@dataclass(frozen=True)
class AgentRuntime:
    """Runtime knobs shared by all local agent CLIs."""

    extra_args: Sequence[str] = ()
    env: Mapping[str, str] = field(default_factory=dict)
    disable_web: bool = True
    isolated_state: bool = True
    timeout_sec: float | None = None
    stream_to_stdout: bool = False
    state_dir: Path | None = None

    def merged(self, **kwargs: object) -> "AgentRuntime":
        values = {
            "extra_args": self.extra_args,
            "env": self.env,
            "disable_web": self.disable_web,
            "isolated_state": self.isolated_state,
            "timeout_sec": self.timeout_sec,
            "stream_to_stdout": self.stream_to_stdout,
            "state_dir": self.state_dir,
        }
        values.update(kwargs)
        return AgentRuntime(**values)
