#!/usr/bin/env python3
"""Patch Harbor to prune task git history before the agent starts.

This is a lightweight alternative to rebuilding every task image.  Harbor still
starts the existing prebuilt image, but immediately after agent installation and
before the solving command it rewrites `/app/.git` to expose only a synthetic
`snapshot` ref at the current base commit.  Remote refs, reflogs, and packed refs
are removed, then unreachable objects are pruned.

Re-run after reinstalling or upgrading Harbor.
"""

from __future__ import annotations

import argparse
from pathlib import Path


HELPER_CODE = r'''
    async def _prune_task_git_history(self, environment: BaseEnvironment) -> None:
        """Remove future/unrelated git refs before the agent can inspect history."""
        if self._get_env("DEPBENCH_DISABLE_GIT_HISTORY_PRUNE") == "1":
            return

        task_env_config = getattr(environment, "task_env_config", None)
        workdir = getattr(task_env_config, "workdir", None) or "/app"
        command = """
set -eu
WORKDIR=%s
mkdir -p /logs/agent
if [ ! -d "$WORKDIR/.git" ]; then
  printf 'no git directory at %%s\n' "$WORKDIR" > /logs/agent/git_history_pruned.txt
  exit 0
fi
cd "$WORKDIR"
commit="$(git rev-parse --verify 'HEAD^{commit}')"
before_refs="$(git for-each-ref --format='%%(refname)' 2>/dev/null | wc -l || true)"
before_size="$(du -sh .git 2>/dev/null | awk '{print $1}' || true)"

# Drop remotes and all ref/reflog metadata that can point past the task snapshot.
for remote in $(git remote 2>/dev/null || true); do
  git remote remove "$remote" 2>/dev/null || true
done
rm -rf .git/refs .git/logs .git/modules
rm -f .git/packed-refs .git/FETCH_HEAD .git/ORIG_HEAD .git/MERGE_HEAD .git/CHERRY_PICK_HEAD .git/REBASE_HEAD
mkdir -p .git/refs/heads .git/logs

git update-ref refs/heads/snapshot "$commit"
git symbolic-ref HEAD refs/heads/snapshot
git reset --hard "$commit" >/dev/null
git reflog expire --expire=now --expire-unreachable=now --all >/dev/null 2>&1 || true
git gc --prune=now >/dev/null 2>&1 || true

after_refs="$(git for-each-ref --format='%%(refname)' 2>/dev/null | wc -l || true)"
after_size="$(du -sh .git 2>/dev/null | awk '{print $1}' || true)"
{
  printf 'commit=%%s\n' "$commit"
  printf 'before_refs=%%s\n' "$before_refs"
  printf 'after_refs=%%s\n' "$after_refs"
  printf 'before_git_size=%%s\n' "$before_size"
  printf 'after_git_size=%%s\n' "$after_size"
} > /logs/agent/git_history_pruned.txt
""" % shlex.quote(str(workdir))
        result = await environment.exec(command=command, user="root", timeout_sec=120)
        if result.return_code != 0:
            raise RuntimeError(
                "Failed to prune DepBench task git history: "
                f"{self._truncate_output(result.stderr or result.stdout)}"
            )
'''


IMPORTS = ["import shlex"]
SETUP_CALL = "        await self._prune_task_git_history(environment)\n"


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

    for import_line in IMPORTS:
        if f"{import_line}\n" not in text:
            if "import functools\n" in text:
                text = text.replace("import functools\n", f"import functools\n{import_line}\n", 1)
            else:
                text = f"{import_line}\n{text}"
            changes.append(f"added {import_line}")

    if "_prune_task_git_history" not in text:
        anchor = "\n    async def _exec(\n"
        if anchor not in text:
            raise RuntimeError("Could not find BaseInstalledAgent._exec anchor")
        text = text.replace(anchor, f"\n{HELPER_CODE}{anchor}", 1)
        changes.append("inserted git history pruning helper")

    if "_prune_task_git_history(environment)" not in text:
        anchor = "        await self._install_task_repo_blocker(environment)\n"
        if anchor in text:
            text = text.replace(anchor, f"{SETUP_CALL}{anchor}", 1)
        else:
            version_anchor = "                    pass  # Version detection is best-effort\n"
            if version_anchor not in text:
                raise RuntimeError("Could not find setup hook anchor")
            text = text.replace(version_anchor, f"{version_anchor}\n{SETUP_CALL}", 1)
        changes.append("added setup hook")

    return text, changes


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-py", type=Path, default=None)
    parser.add_argument("--check", action="store_true", help="fail if patch is not present")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    target = args.base_py or default_base_py()
    original = target.read_text(encoding="utf-8")
    patched, changes = patch_text(original)

    if args.check:
        if changes:
            print(f"{target} is missing patch pieces: {', '.join(changes)}")
            return 1
        print(f"{target} already has the DepBench git history pruner patch")
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
