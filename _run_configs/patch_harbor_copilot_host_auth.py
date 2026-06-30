#!/usr/bin/env python3
"""Patch Harbor Copilot CLI wrapper to inject host Copilot auth explicitly."""

from __future__ import annotations

import argparse
from pathlib import Path


ANCHOR = '''        # Register skills
        skills_command = self._build_register_skills_command()
'''

INJECT = '''        # DepBench: prefer the real host auth env over any serialized/masked
        # AgentConfig env values.  Harbor writes redacted env values into
        # config.json, and some versions pass those through to wrappers.  The
        # host process environment keeps the actual OAuth/PAT token.
        host_token = (
            os.environ.get("COPILOT_GITHUB_TOKEN")
            or os.environ.get("GH_TOKEN")
            or os.environ.get("GITHUB_TOKEN")
        )
        if host_token:
            env.update(
                {
                    "COPILOT_GITHUB_TOKEN": host_token,
                    "GH_TOKEN": host_token,
                    "GITHUB_TOKEN": host_token,
                }
            )
        try:
            (self.logs_dir / "copilot_auth_env.txt").write_text(
                "COPILOT_GITHUB_TOKEN=%s\\nGH_TOKEN=%s\\nGITHUB_TOKEN=%s\\n"
                % (
                    "set" if env.get("COPILOT_GITHUB_TOKEN") else "unset",
                    "set" if env.get("GH_TOKEN") else "unset",
                    "set" if env.get("GITHUB_TOKEN") else "unset",
                ),
                encoding="utf-8",
            )
        except Exception:
            pass

        # Register skills
        skills_command = self._build_register_skills_command()
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
    if "DepBench: prefer the real host auth env" in text:
        return text, []
    if ANCHOR not in text:
        raise RuntimeError("Could not find Copilot skills anchor")
    return text.replace(ANCHOR, INJECT, 1), ["injected host Copilot auth env"]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--copilot-py", type=Path, default=None)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    target = args.copilot_py or default_copilot_py()
    original = target.read_text(encoding="utf-8")
    patched, changes = patch_text(original)
    if args.check:
        if changes:
            print(f"{target} is missing patch pieces: {', '.join(changes)}")
            return 1
        print(f"{target} already has the DepBench host Copilot auth patch")
        return 0
    if not changes:
        print(f"{target} already patched")
        return 0
    print(f"Patching {target}: {', '.join(changes)}")
    target.write_text(patched, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
