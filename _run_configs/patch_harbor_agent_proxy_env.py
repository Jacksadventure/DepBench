#!/usr/bin/env python3
"""Patch Harbor so agent commands inherit a configured proxy URL.

Set `DEPBENCH_AGENT_PROXY_URL` in the host environment before running Harbor.
The patch copies that value into HTTP(S)_PROXY/ALL_PROXY for agent commands
after installation and before the solving command.  This is meant to be used
with `_run_configs/depbench_github_guard_proxy.py`.
"""

from __future__ import annotations

import argparse
from pathlib import Path


HELPER_CODE = r'''
    async def _install_depbench_agent_proxy_env(self, environment: BaseEnvironment) -> None:
        proxy_url = self._get_env("DEPBENCH_AGENT_PROXY_URL")
        if not proxy_url or self._get_env("DEPBENCH_DISABLE_AGENT_PROXY") == "1":
            return
        no_proxy = self._get_env("DEPBENCH_AGENT_NO_PROXY") or (
            "127.0.0.1,localhost,::1,172.100.216.1,host.docker.internal"
        )
        for key in (
            "HTTP_PROXY",
            "HTTPS_PROXY",
            "ALL_PROXY",
            "http_proxy",
            "https_proxy",
            "all_proxy",
        ):
            self._extra_env[key] = proxy_url
        self._extra_env["NO_PROXY"] = no_proxy
        self._extra_env["no_proxy"] = no_proxy
        try:
            (self.logs_dir / "agent_proxy.txt").write_text(
                f"proxy={proxy_url}\nno_proxy={no_proxy}\n",
                encoding="utf-8",
            )
        except Exception:
            pass
'''


SETUP_CALL = "        await self._install_depbench_agent_proxy_env(environment)\n"


def default_base_py() -> Path:
    candidates = sorted(
        Path.home().glob(
            ".local/share/uv/tools/harbor/lib/python*/site-packages/"
            "harbor/agents/installed/base.py"
        )
    )
    if not candidates:
        raise FileNotFoundError("Could not find Harbor installed base.py")
    return candidates[-1]


def patch_text(text: str) -> tuple[str, list[str]]:
    changes: list[str] = []
    if "_install_depbench_agent_proxy_env" not in text:
        anchor = "\n    async def _exec(\n"
        if anchor not in text:
            raise RuntimeError("Could not find BaseInstalledAgent._exec anchor")
        text = text.replace(anchor, f"\n{HELPER_CODE}{anchor}", 1)
        changes.append("inserted proxy env helper")
    if "_install_depbench_agent_proxy_env(environment)" not in text:
        for anchor in (
            "        await self._prune_task_git_history(environment)\n",
            "        await self._install_task_repo_blocker(environment)\n",
            "                    pass  # Version detection is best-effort\n",
        ):
            if anchor in text:
                text = text.replace(anchor, f"{SETUP_CALL}{anchor}", 1)
                changes.append("added setup hook")
                break
        else:
            raise RuntimeError("Could not find setup hook anchor")
    return text, changes


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-py", type=Path, default=None)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    target = args.base_py or default_base_py()
    original = target.read_text(encoding="utf-8")
    patched, changes = patch_text(original)
    if args.check:
        if changes:
            print(f"{target} is missing patch pieces: {', '.join(changes)}")
            return 1
        print(f"{target} already has the DepBench agent proxy env patch")
        return 0
    if not changes:
        print(f"{target} already patched")
        return 0
    print(f"Patching {target}: {', '.join(changes)}")
    if not args.dry_run:
        target.write_text(patched, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
