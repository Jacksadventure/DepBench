#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""Publish the source-build benchmark to a dedicated Hugging Face branch."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from huggingface_hub import HfApi


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_TASKS = 201
DEFAULT_REPO_ID = "ZijiantheJack/DepBench"
DEFAULT_BRANCH = "source-build-main"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require_complete_audits() -> None:
    for path, status_field in (
        (ROOT / "analysis/source_build_audit_201.csv", "build_status"),
        (ROOT / "analysis/source_commit_audit_201.csv", "fetch_status"),
    ):
        rows = list(csv.DictReader(path.open(encoding="utf-8")))
        if (
            len(rows) != EXPECTED_TASKS
            or len({row["task"] for row in rows}) != EXPECTED_TASKS
            or any(row[status_field] != "pass" or row["error"] for row in rows)
        ):
            raise SystemExit(f"incomplete source-build audit: {path}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-id", default=DEFAULT_REPO_ID)
    parser.add_argument("--branch", default=DEFAULT_BRANCH)
    parser.add_argument(
        "--archive",
        type=Path,
        default=ROOT / "depbench-main-source-build201.tar.gz",
    )
    args = parser.parse_args()

    archive = args.archive.resolve()
    if not archive.is_file():
        raise SystemExit(f"archive is missing: {archive}")
    require_complete_audits()
    archive_digest = sha256(archive)

    api = HfApi()
    api.create_branch(
        repo_id=args.repo_id,
        repo_type="dataset",
        branch=args.branch,
        exist_ok=True,
    )
    with tempfile.TemporaryDirectory(prefix="depbench-hf-source-build-") as temporary:
        staging = Path(temporary)
        shutil.copytree(ROOT / "dataset", staging / "dataset")
        shutil.copytree(ROOT / "analysis", staging / "analysis")
        (staging / "repro").mkdir()
        shutil.copy2(ROOT / "repro/TASK_SCHEMA.md", staging / "repro/TASK_SCHEMA.md")
        shutil.copy2(ROOT / "repro/HUGGING_FACE_DATASET_CARD.md", staging / "README.md")
        shutil.copy2(archive, staging / archive.name)
        manifest = {
            "archive": archive.name,
            "archive_sha256": archive_digest,
            "base_images": 41,
            "build_mode": "local_source_build",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "source_build_audit": "analysis/source_build_audit_201.csv",
            "source_commit_audit": "analysis/source_commit_audit_201.csv",
            "source_metadata": "analysis/task_source_builds.csv",
            "tasks": EXPECTED_TASKS,
        }
        (staging / "MANIFEST.json").write_text(
            json.dumps(manifest, indent=2) + "\n",
            encoding="utf-8",
        )
        result = api.upload_folder(
            repo_id=args.repo_id,
            repo_type="dataset",
            revision=args.branch,
            folder_path=staging,
            commit_message="Publish 201-task source-build benchmark",
            commit_description=(
                "Replace prebuilt task-image references with Dockerfiles that "
                "clone canonical repositories and checkout fixed commits."
            ),
            delete_patterns=[
                "dataset/**",
                "analysis/**",
                "repro/**",
                "README.md",
                "MANIFEST.json",
                "*.tar.gz",
            ],
        )

    print(f"repo={args.repo_id}")
    print(f"branch={args.branch}")
    print(f"commit={result.oid}")
    print(f"archive={archive.name}")
    print(f"sha256={archive_digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
