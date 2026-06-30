from __future__ import annotations

import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from .artifacts import copy_globs


def _run(cmd: Sequence[str], *, cwd: Path | None = None) -> str:
    proc = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True, check=False)
    if proc.returncode != 0:
        joined = " ".join(cmd)
        raise RuntimeError(
            f"command failed ({proc.returncode}): {joined}\n"
            f"stdout:\n{proc.stdout}\nstderr:\n{proc.stderr}"
        )
    return proc.stdout


@dataclass(frozen=True)
class Workspace:
    path: Path
    source_repo: Path | None = None
    base_commit: str | None = None
    owned: bool = True


@dataclass(frozen=True)
class WorkspaceSpec:
    """Description of how to prepare an agent workspace."""

    repo_path: Path | None = None
    base_commit: str | None = None
    existing_path: Path | None = None
    keep_history_cutoff: bool = True
    clean: bool = True
    copy_paths: Sequence[str] = ()

    @classmethod
    def from_local_repo(
        cls,
        repo_path: Path | str,
        *,
        base_commit: str,
        keep_history_cutoff: bool = True,
        clean: bool = True,
    ) -> "WorkspaceSpec":
        return cls(
            repo_path=Path(repo_path),
            base_commit=base_commit,
            keep_history_cutoff=keep_history_cutoff,
            clean=clean,
        )

    @classmethod
    def existing(cls, path: Path | str, *, clean: bool = False) -> "WorkspaceSpec":
        return cls(existing_path=Path(path), clean=clean)

    def prepare(self, dest: Path) -> Workspace:
        dest = dest.resolve()
        if self.existing_path is not None:
            path = self.existing_path.resolve()
            if self.clean:
                _run(["git", "reset", "--hard"], cwd=path)
                _run(["git", "clean", "-fdx"], cwd=path)
            if self.copy_paths:
                copy_globs(self.copy_paths, src_root=path, dst_root=path)
            return Workspace(path=path, owned=False)

        if self.repo_path is None or self.base_commit is None:
            raise ValueError("WorkspaceSpec needs either existing_path or repo_path+base_commit")

        repo_path = self.repo_path.resolve()
        if dest.exists():
            raise FileExistsError(dest)
        dest.parent.mkdir(parents=True, exist_ok=True)

        _run(["git", "rev-parse", "--verify", f"{self.base_commit}^{{commit}}"], cwd=repo_path)
        _run(["git", "clone", "--no-hardlinks", "--no-checkout", str(repo_path), str(dest)])
        _run(["git", "checkout", "--detach", self.base_commit], cwd=dest)

        if self.keep_history_cutoff:
            self._prune_to_snapshot(dest, self.base_commit)
        if self.clean:
            _run(["git", "reset", "--hard", self.base_commit], cwd=dest)
            _run(["git", "clean", "-fdx"], cwd=dest)
        if self.copy_paths:
            copy_globs(self.copy_paths, src_root=repo_path, dst_root=dest)

        return Workspace(path=dest, source_repo=repo_path, base_commit=self.base_commit)

    @staticmethod
    def _prune_to_snapshot(workspace: Path, commit: str) -> None:
        """Keep normal git history reachable from commit and prune future refs."""

        refs = _run(["git", "for-each-ref", "--format=%(refname)"], cwd=workspace)
        for ref in refs.splitlines():
            if ref.strip():
                _run(["git", "update-ref", "-d", ref.strip()], cwd=workspace)
        _run(["git", "update-ref", "refs/heads/snapshot", commit], cwd=workspace)
        _run(["git", "symbolic-ref", "HEAD", "refs/heads/snapshot"], cwd=workspace)
        _run(["git", "reset", "--hard", commit], cwd=workspace)
        _run(["git", "reflog", "expire", "--expire=now", "--expire-unreachable=now", "--all"], cwd=workspace)
        _run(["git", "gc", "--prune=now"], cwd=workspace)


def remove_workspace(workspace: Workspace) -> None:
    if workspace.owned and workspace.path.exists():
        shutil.rmtree(workspace.path)
