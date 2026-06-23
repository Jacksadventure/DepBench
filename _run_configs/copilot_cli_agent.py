"""Versioned Copilot CLI adapter for Harbor benchmark configs.

Harbor already ships the actual Copilot CLI implementation as
``harbor.agents.installed.copilot_cli:CopilotCli``.  This thin subclass gives
benchmark configs a repository-owned import path, while keeping authentication
and version pinning in the JSON config (for example mounting
``~/.copilot/config.json`` read-only and setting ``COPILOT_HOME``).
"""

from __future__ import annotations

from harbor.agents.installed.copilot_cli import CopilotCli


class CopilotCliHostAuth(CopilotCli):
    """Copilot CLI adapter alias used by DepBench run configs."""

