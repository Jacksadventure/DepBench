#!/usr/bin/env python3
"""Patch Harbor's Copilot CLI wrapper to forward auth env from agent config.

Harbor's stock Copilot CLI wrapper read only `os.environ` and passed only
`GITHUB_TOKEN` into the container command.  For generated configs that set
`agent.env` (stored in `self._extra_env`), Copilot therefore reported
"No authentication information found".  This patch switches token lookup to
`self._get_env()` and forwards all three accepted variable names.
"""

from __future__ import annotations

import argparse
from pathlib import Path


OLD = '''        token = (
            os.environ.get("COPILOT_GITHUB_TOKEN")
            or os.environ.get("GH_TOKEN")
            or os.environ.get("GITHUB_TOKEN")
        )
        env: dict[str, str] = {"GITHUB_TOKEN": token} if token else {}
'''

NEW = '''        token = (
            self._get_env("COPILOT_GITHUB_TOKEN")
            or self._get_env("GH_TOKEN")
            or self._get_env("GITHUB_TOKEN")
        )
        env: dict[str, str] = {}
        if token:
            env.update(
                {
                    "COPILOT_GITHUB_TOKEN": token,
                    "GH_TOKEN": token,
                    "GITHUB_TOKEN": token,
                }
            )
'''


def default_copilot_py() -> Path:
    candidates = sorted(
        Path.home().glob(
            ".local/share/uv/tools/harbor/lib/python*/site-packages/"
            "harbor/agents/installed/copilot_cli.py"
        )
    )
    if not candidates:
        raise FileNotFoundError("Could not find Harbor installed copilot_cli.py")
    return candidates[-1]


def patch_text(text: str) -> tuple[str, list[str]]:
    if NEW in text:
        return text, []
    if OLD not in text:
        raise RuntimeError("Could not find Copilot auth env block to patch")
    return text.replace(OLD, NEW, 1), ["forwarded COPILOT_GITHUB_TOKEN/GH_TOKEN/GITHUB_TOKEN from _extra_env"]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--copilot-py", type=Path, default=None)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    target = args.copilot_py or default_copilot_py()
    original = target.read_text(encoding="utf-8")
    patched, changes = patch_text(original)
    if args.check:
        if changes:
            print(f"{target} is missing patch pieces: {', '.join(changes)}")
            return 1
        print(f"{target} already has the DepBench Copilot auth env patch")
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
