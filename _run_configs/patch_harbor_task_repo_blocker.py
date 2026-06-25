#!/usr/bin/env python3
"""Patch Harbor so each trial blocks access to its own upstream GitHub repo.

This script makes the local Harbor installation install a per-task repository
guard after agent installation and before the agent starts solving.  The guard
blocks common shell tools (`git`, `curl`, `wget`, and `gh`) from accessing the
exact GitHub repository associated with the current task, while leaving other
repositories and dependency documentation reachable.

The patch is intentionally local to the Harbor tool installation.  Re-run it
after reinstalling or upgrading Harbor.
"""

from __future__ import annotations

import argparse
from pathlib import Path


HELPER_CODE = r'''
    def _infer_task_repo_from_logs_dir(self) -> tuple[str, str] | None:
        # DepBench task directories are named owner__repo__pr. Prefer an
        # explicit Upstream PR URL from instruction.md when available.
        trial_dir = self.logs_dir.parent
        task_path: Path | None = None

        config_path = trial_dir / "config.json"
        if config_path.exists():
            try:
                config = json.loads(config_path.read_text(encoding="utf-8"))
                raw_path = config.get("task", {}).get("path")
                if raw_path:
                    task_path = Path(raw_path)
            except Exception:
                task_path = None

        if task_path:
            instruction_path = task_path / "instruction.md"
            if instruction_path.exists():
                try:
                    instruction = instruction_path.read_text(
                        encoding="utf-8", errors="ignore"
                    )
                    match = re.search(
                        r"https://github\.com/([^/\s]+)/([^/\s]+)/pull/\d+",
                        instruction,
                    )
                    if match:
                        return match.group(1), match.group(2)
                except Exception:
                    pass

            folder = task_path.name
        else:
            folder = trial_dir.name

        parts = folder.split("__")
        if len(parts) >= 2 and parts[0] and parts[1]:
            return parts[0], parts[1]
        return None

    async def _install_task_repo_blocker(self, environment: BaseEnvironment) -> None:
        # Blocks common shell-level attempts to inspect the exact upstream task
        # repository, while preserving access to other repositories and docs.
        if self._get_env("DEPBENCH_DISABLE_TASK_REPO_BLOCK") == "1":
            return

        repo = self._infer_task_repo_from_logs_dir()
        if not repo:
            raise RuntimeError(
                "Could not infer task repository for DepBench repo blocker. "
                "Set DEPBENCH_DISABLE_TASK_REPO_BLOCK=1 to bypass."
            )

        owner, name = repo
        owner_q = shlex.quote(owner)
        repo_q = shlex.quote(name)
        command = f"""
set -euo pipefail
OWNER={owner_q}
REPO={repo_q}
OWNER_LC="$(printf '%s' "$OWNER" | tr '[:upper:]' '[:lower:]')"
REPO_LC="$(printf '%s' "$REPO" | tr '[:upper:]' '[:lower:]')"
REAL_DIR=/usr/local/lib/depbench-real-bin
mkdir -p "$REAL_DIR" /usr/local/bin /logs/agent
printf '%s/%s\n' "$OWNER" "$REPO" > /logs/agent/blocked_repo.txt

cat > /usr/local/bin/depbench-blocked-repo-check <<'GUARD'
#!/usr/bin/env bash
set -euo pipefail
OWNER_LC="${DEPBENCH_BLOCK_OWNER_LC:?}"
REPO_LC="${DEPBENCH_BLOCK_REPO_LC:?}"
TOOL="${DEPBENCH_NETGUARD_TOOL:-}"

check_text() {{
  local text="${{1:-}}"
  local lower
  lower="$(printf '%s' "$text" | tr '[:upper:]' '[:lower:]')"
  lower="${{lower%.git}}"
  if [[ "$lower" == *"github.com/${{OWNER_LC}}/${{REPO_LC}}"* ]] ||
     [[ "$lower" == *"api.github.com/repos/${{OWNER_LC}}/${{REPO_LC}}"* ]] ||
     [[ "$lower" == *"raw.githubusercontent.com/${{OWNER_LC}}/${{REPO_LC}}"* ]] ||
     [[ "$lower" == *"codeload.github.com/${{OWNER_LC}}/${{REPO_LC}}"* ]] ||
     [[ "$lower" == *"${{OWNER_LC}}%2f${{REPO_LC}}"* ]]; then
    echo "DepBench policy: access to task repository ${{OWNER_LC}}/${{REPO_LC}} is blocked during agent solving." >&2
    exit 86
  fi
}}

for arg in "$@"; do
  check_text "$arg"
done

if [[ "$TOOL" == "git" ]]; then
  subcmd="${{1:-}}"
  case "$subcmd" in
    clone|fetch|pull|push|ls-remote|remote|submodule)
      if [[ -x /usr/local/lib/depbench-real-bin/git ]]; then
        remotes="$(/usr/local/lib/depbench-real-bin/git remote -v 2>/dev/null || true)"
        check_text "$remotes"
      fi
      ;;
  esac
fi
GUARD
chmod +x /usr/local/bin/depbench-blocked-repo-check

for tool in git curl wget gh; do
  existing="$(command -v "$tool" 2>/dev/null || true)"
  if [[ -n "$existing" && "$existing" != "/usr/local/bin/$tool" ]]; then
    ln -sf "$existing" "$REAL_DIR/$tool"
  elif [[ -n "$existing" && "$existing" == "/usr/local/bin/$tool" && ! -e "$REAL_DIR/$tool" ]]; then
    cp -a "$existing" "$REAL_DIR/$tool"
  fi

  cat > "/usr/local/bin/$tool" <<WRAP
#!/usr/bin/env bash
set -euo pipefail
export DEPBENCH_BLOCK_OWNER_LC="$OWNER_LC"
export DEPBENCH_BLOCK_REPO_LC="$REPO_LC"
export DEPBENCH_NETGUARD_TOOL="$tool"
/usr/local/bin/depbench-blocked-repo-check "\$@"
for candidate in "/usr/local/lib/depbench-real-bin/$tool" "/usr/bin/$tool" "/bin/$tool" "/usr/local/sbin/$tool" "/usr/sbin/$tool"; do
  if [[ -x "\$candidate" && "\$candidate" != "\$0" ]]; then
    exec "\$candidate" "\$@"
  fi
done
echo "DepBench policy wrapper could not find real $tool binary" >&2
exit 127
WRAP
  chmod +x "/usr/local/bin/$tool"
done

if [[ -x "$REAL_DIR/git" ]]; then
  "$REAL_DIR/git" config --system --add url."https://depbench-blocked.invalid/${{OWNER_LC}}/${{REPO_LC}}".insteadOf "https://github.com/${{OWNER}}/${{REPO}}"
  "$REAL_DIR/git" config --system --add url."https://depbench-blocked.invalid/${{OWNER_LC}}/${{REPO_LC}}".insteadOf "https://github.com/${{OWNER}}/${{REPO}}.git"
  "$REAL_DIR/git" config --system --add url."ssh://depbench-blocked.invalid/${{OWNER_LC}}/${{REPO_LC}}".insteadOf "git@github.com:${{OWNER}}/${{REPO}}.git"
fi
"""
        result = await environment.exec(command=command, user="root", timeout_sec=60)
        if result.return_code != 0:
            raise RuntimeError(
                "Failed to install DepBench task repository blocker: "
                f"{self._truncate_output(result.stderr or result.stdout)}"
            )
'''


IMPORTS = ["import json", "import re", "import shlex"]
SETUP_CALL = "        await self._install_task_repo_blocker(environment)\n"


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

    if "_infer_task_repo_from_logs_dir" not in text:
        anchor = "\n    async def _exec(\n"
        if anchor not in text:
            raise RuntimeError("Could not find BaseInstalledAgent._exec anchor")
        text = text.replace(anchor, f"\n{HELPER_CODE}{anchor}", 1)
        changes.append("inserted repo blocker helpers")

    if "_install_task_repo_blocker(environment)" not in text:
        anchor = "                    pass  # Version detection is best-effort\n"
        if anchor not in text:
            raise RuntimeError("Could not find setup version-detection anchor")
        text = text.replace(anchor, f"{anchor}\n{SETUP_CALL}", 1)
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
        print(f"{target} already has the DepBench task repo blocker patch")
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
