#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import tarfile
import tempfile
from pathlib import Path

from huggingface_hub import hf_hub_download


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REPO_ID = "Depbench/build_from_source"
DEFAULT_REVISION = "3dfc6d08c8c83ec578f32c175cb7be2b8d5bec93"
ARCHIVE_FILENAME = "depbench-main-source-build201.tar.gz"
ARCHIVE_SHA256 = "00f641612d40e4d5fe9550a7f8eaee945277afb5a20bebab42028140d20b658d"
EXPECTED_TASKS = 201


def validate_dataset(destination: Path, expected_tasks: int) -> None:
    summary_path = destination / "dataset/task_summary.json"
    tasks_path = destination / "dataset/tasks"
    if not summary_path.is_file() or not tasks_path.is_dir():
        raise SystemExit(f"incomplete benchmark download under {destination / 'dataset'}")

    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    summary_tasks = {row["folder"] for row in summary}
    directory_tasks = {path.name for path in tasks_path.iterdir() if path.is_dir()}
    if len(summary) != expected_tasks or summary_tasks != directory_tasks:
        raise SystemExit(
            "benchmark validation failed: "
            f"summary={len(summary)} directories={len(directory_tasks)}"
        )


def extract_archive(archive_path: Path, destination: Path) -> None:
    with tarfile.open(archive_path, "r:gz") as archive:
        for member in archive.getmembers():
            member_path = (destination / member.name).resolve()
            if (
                not member_path.is_relative_to(destination.resolve())
                or member.issym()
                or member.islnk()
                or member.isdev()
            ):
                raise SystemExit(f"unsafe archive entry: {member.name}")
        archive.extractall(destination)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Download the directory-format DepBench benchmark from Hugging Face."
    )
    parser.add_argument("--repo-id", default=DEFAULT_REPO_ID)
    parser.add_argument("--revision", default=DEFAULT_REVISION)
    parser.add_argument(
        "--destination",
        type=Path,
        default=ROOT,
        help="directory that will contain dataset/ (default: release root)",
    )
    args = parser.parse_args()

    destination = args.destination.expanduser().resolve()
    destination.mkdir(parents=True, exist_ok=True)
    archive_path = Path(
        hf_hub_download(
            repo_id=args.repo_id,
            repo_type="dataset",
            revision=args.revision,
            filename=ARCHIVE_FILENAME,
        )
    )
    archive_sha256 = hashlib.sha256(archive_path.read_bytes()).hexdigest()
    if archive_sha256 != ARCHIVE_SHA256:
        raise SystemExit(
            f"archive checksum mismatch: {archive_sha256} != {ARCHIVE_SHA256}"
        )

    with tempfile.TemporaryDirectory(
        prefix=".depbench-download-", dir=destination
    ) as temporary_directory:
        temporary_path = Path(temporary_directory)
        extract_archive(archive_path, temporary_path)
        validate_dataset(temporary_path, EXPECTED_TASKS)

        destination_dataset = destination / "dataset"
        if destination_dataset.is_symlink():
            raise SystemExit(f"refusing to replace symlink: {destination_dataset}")
        if destination_dataset.exists():
            shutil.rmtree(destination_dataset)
        shutil.move(temporary_path / "dataset", destination_dataset)

    validate_dataset(destination, EXPECTED_TASKS)
    print(
        f"DepBench ready: {EXPECTED_TASKS} tasks in "
        f"{destination / 'dataset/tasks'} ({args.repo_id}@{args.revision})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
