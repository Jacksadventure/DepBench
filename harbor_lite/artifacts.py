from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Iterable


def _is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def copy_globs(
    patterns: Iterable[str],
    *,
    src_root: Path,
    dst_root: Path,
    clean: bool = False,
) -> list[dict[str, str]]:
    """Copy globbed files or directories while preserving relative paths."""

    src_root = src_root.resolve()
    dst_root.mkdir(parents=True, exist_ok=True)
    if clean and dst_root.exists():
        shutil.rmtree(dst_root)
        dst_root.mkdir(parents=True, exist_ok=True)

    manifest: list[dict[str, str]] = []
    seen: set[Path] = set()
    for pattern in patterns:
        matches = sorted(src_root.glob(pattern))
        for src in matches:
            src = src.resolve()
            if src in seen or not _is_relative_to(src, src_root):
                continue
            seen.add(src)
            rel = src.relative_to(src_root)
            dst = dst_root / rel
            if src.is_dir():
                shutil.copytree(src, dst, dirs_exist_ok=True, symlinks=True)
                kind = "directory"
            elif src.is_file() or src.is_symlink():
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst, follow_symlinks=False)
                kind = "file"
            else:
                continue
            manifest.append(
                {
                    "source": str(src),
                    "destination": rel.as_posix(),
                    "type": kind,
                }
            )
    return manifest


def write_manifest(path: Path, entries: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(entries, indent=2) + "\n")


def tail_text(path: Path, *, lines: int = 200) -> str:
    if not path.exists():
        return ""
    data = path.read_text(errors="replace").splitlines()
    return "\n".join(data[-lines:]) + ("\n" if data else "")


def write_exception_tail(
    path: Path,
    *,
    log_path: Path,
    exit_code: int | None,
    lines: int = 200,
) -> None:
    body = [
        f"Agent exited with code {exit_code}.",
        "",
        f"Last {lines} lines from {log_path}:",
        "",
        tail_text(log_path, lines=lines),
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(body))
