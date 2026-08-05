#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""Create a deterministic archive of the 201-task source-build dataset."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import tarfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_TASKS = 201
EXCLUDED_TASKS = {
    "databricks__cli__1326",
    "nearform__brokeneck__820",
}


def add_path(archive: tarfile.TarFile, path: Path, arcname: str) -> None:
    if path.is_symlink():
        raise SystemExit(f"refusing to package symlink: {path}")
    info = archive.gettarinfo(str(path), arcname)
    info.uid = 0
    info.gid = 0
    info.uname = "root"
    info.gname = "root"
    info.mtime = 0
    if path.is_file():
        with path.open("rb") as handle:
            archive.addfile(info, handle)
    else:
        archive.addfile(info)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "depbench-main-source-build201.tar.gz",
    )
    args = parser.parse_args()

    dataset = ROOT / "dataset"
    tasks = dataset / "tasks"
    summary = json.loads((dataset / "task_summary.json").read_text(encoding="utf-8"))
    task_names = {path.name for path in tasks.iterdir() if path.is_dir()}
    if (
        len(task_names) != EXPECTED_TASKS
        or {row["folder"] for row in summary} != task_names
        or task_names & EXCLUDED_TASKS
    ):
        raise SystemExit("dataset is not the 201-task main source-build snapshot")
    for task in task_names:
        task_dir = tasks / task
        if not (task_dir / "environment/Dockerfile").is_file():
            raise SystemExit(f"{task}: Dockerfile is missing")
        if (task_dir / "environment/docker-compose.yaml").exists():
            raise SystemExit(f"{task}: placeholder compose file remains")
        if "docker_image" in (task_dir / "task.toml").read_text(encoding="utf-8"):
            raise SystemExit(f"{task}: prebuilt image reference remains")

    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("wb") as raw:
        with gzip.GzipFile(fileobj=raw, mode="wb", mtime=0) as compressed:
            with tarfile.open(fileobj=compressed, mode="w") as archive:
                for path in [dataset, *sorted(dataset.rglob("*"))]:
                    add_path(
                        archive,
                        path,
                        path.relative_to(ROOT).as_posix(),
                    )

    digest = hashlib.sha256(output.read_bytes()).hexdigest()
    print(f"{output}\nsha256={digest}\ntasks={EXPECTED_TASKS}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
