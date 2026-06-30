"""Local coding-agent adapters."""

from .base import AgentResult, LocalAgent
from .claude import ClaudeAgent
from .codex import CodexAgent
from .gemini import GeminiAgent
from .opencode import OpenCodeAgent
from .qwen import QwenAgent

__all__ = [
    "AgentResult",
    "ClaudeAgent",
    "CodexAgent",
    "GeminiAgent",
    "LocalAgent",
    "OpenCodeAgent",
    "QwenAgent",
]
