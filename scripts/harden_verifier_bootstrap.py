#!/usr/bin/env python3
"""Make verifier bootstrap failures distinct from graded test failures."""

import argparse
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("tasks_root", type=Path)
    parser.add_argument(
        "--active-tasks-root",
        type=Path,
        help="Use directory names from this task root as the active task set.",
    )
    return parser.parse_args()


def active_task_names(tasks_root: Path, active_tasks_root: Path | None) -> list[str]:
    source = active_tasks_root or tasks_root
    return sorted(path.name for path in source.iterdir() if path.is_dir())


def harden(test_script: Path) -> bool:
    text = test_script.read_text(encoding="utf-8")
    lines = text.splitlines()
    if len(lines) < 3 or not lines[2].startswith("# harbor-canary GUID "):
        raise ValueError(f"Unexpected verifier header: {test_script}")

    hardened = "\n".join(
        [
            lines[0],
            lines[1],
            lines[2],
            "",
            "set -euo pipefail",
            "",
            "apt-get update && apt-get install -y curl ca-certificates "
            "&& rm -rf /var/lib/apt/lists/*",
            "",
            "curl -LsSf https://astral.sh/uv/0.9.7/install.sh | sh",
            "",
            'source "$HOME/.local/bin/env"',
            "",
            "set +e",
            "uvx \\",
            "  --with pytest==8.4.1 \\",
            "  --with pytest-json-ctrf==0.3.5 \\",
            "  pytest --ctrf /logs/verifier/ctrf.json "
            "/tests/test_state.py -rA",
            "rc=$?",
            "set -e",
            "",
            'if [ "$rc" -eq 0 ]; then',
            "  echo 1 > /logs/verifier/reward.txt",
            "else",
            "  echo 0 > /logs/verifier/reward.txt",
            "fi",
            "",
            'exit "$rc"',
            "",
        ]
    )
    if text == hardened:
        return False
    test_script.write_text(hardened, encoding="utf-8")
    return True


def main() -> None:
    args = parse_args()
    changed = 0
    names = active_task_names(args.tasks_root, args.active_tasks_root)
    for name in names:
        test_script = args.tasks_root / name / "tests" / "test.sh"
        if not test_script.is_file():
            raise FileNotFoundError(test_script)
        changed += harden(test_script)
    print(f"Hardened {changed}/{len(names)} verifier bootstrap scripts")


if __name__ == "__main__":
    main()
