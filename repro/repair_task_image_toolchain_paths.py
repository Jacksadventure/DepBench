#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""Add login-shell-visible toolchain entry points to task images."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path


IMAGE_PATTERN = re.compile(r'^docker_image\s*=\s*"([^"]+)"\s*$')
RUST_DOCKERFILE = r"""ARG BASE_IMAGE
FROM ${BASE_IMAGE}
RUN set -eux; \
    for tool in cargo rustc rustup rustdoc rustfmt cargo-fmt cargo-clippy clippy-driver; do \
        source_path=""; \
        for directory in /usr/local/cargo/bin /root/.cargo/bin; do \
            if [ -e "${directory}/${tool}" ]; then \
                source_path="${directory}/${tool}"; \
                break; \
            fi; \
        done; \
        if [ -n "${source_path}" ]; then \
            ln -sf "${source_path}" "/usr/local/bin/${tool}"; \
        fi; \
    done; \
    bash -lc 'command -v cargo; cargo --version; command -v rustc; rustc --version'
"""
JAVA_DOCKERFILE = r"""ARG BASE_IMAGE
FROM ${BASE_IMAGE}
ENV JAVA_HOME=/opt/java/openjdk
RUN set -eux; \
    test -x "${JAVA_HOME}/bin/java"; \
    for source_path in "${JAVA_HOME}"/bin/*; do \
        if [ -f "${source_path}" ] && [ -x "${source_path}" ]; then \
            ln -sf "${source_path}" "/usr/local/bin/$(basename "${source_path}")"; \
        fi; \
    done; \
    bash -lc 'test "${JAVA_HOME}" = /opt/java/openjdk; command -v java; java -version; command -v mvn; mvn -version'
"""
GO_DOCKERFILE = r"""ARG BASE_IMAGE
FROM ${BASE_IMAGE}
RUN set -eux; \
    test -x /usr/local/go/bin/go; \
    for source_path in /usr/local/go/bin/*; do \
        if [ -f "${source_path}" ] && [ -x "${source_path}" ]; then \
            ln -sf "${source_path}" "/usr/local/bin/$(basename "${source_path}")"; \
        fi; \
    done; \
    bash -lc 'command -v go; go version; command -v gofmt'
"""


def run(
    command: list[str],
    *,
    input_text: str | None = None,
) -> str:
    result = subprocess.run(
        command,
        input=input_text,
        text=True,
        check=True,
        capture_output=True,
    )
    return result.stdout.strip()


def task_image(dataset: Path, task: str) -> str:
    task_toml = dataset / task / "task.toml"
    for line in task_toml.read_text(encoding="utf-8").splitlines():
        match = IMAGE_PATTERN.match(line.strip())
        if match:
            return match.group(1)
    raise SystemExit(f"{task_toml}: docker_image is missing")


def source_digest(image: str) -> str:
    run(["docker", "pull", image])
    digests = run(
        [
            "docker",
            "image",
            "inspect",
            image,
            "--format",
            "{{json .RepoDigests}}",
        ]
    )
    values = json.loads(digests)
    if not values:
        raise SystemExit(f"{image}: no repository digest after pull")
    repository = image.rsplit(":", 1)[0]
    return next(
        (value for value in values if value.startswith(f"{repository}@")),
        values[0],
    )


def verify(image: str, toolchain: str) -> None:
    if toolchain == "rust":
        command = (
            "test \"$(command -v cargo)\" = /usr/local/bin/cargo; "
            "test \"$(command -v rustc)\" = /usr/local/bin/rustc; "
            "cargo --version; rustc --version"
        )
    elif toolchain == "java":
        command = (
            "test \"$JAVA_HOME\" = /opt/java/openjdk; "
            "test \"$(command -v java)\" = /usr/local/bin/java; "
            "java -version; mvn -version"
        )
    else:
        command = (
            "test \"$(command -v go)\" = /usr/local/bin/go; "
            "test \"$(command -v gofmt)\" = /usr/local/bin/gofmt; "
            "go version"
        )
    run(
        [
            "docker",
            "run",
            "--rm",
            "--entrypoint",
            "/bin/bash",
            image,
            "-lc",
            command,
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--tasks-file", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument(
        "--toolchain",
        choices=("rust", "java", "go"),
        required=True,
    )
    parser.add_argument(
        "--staging-repository",
        default="depbench-rust-path-fix",
    )
    parser.add_argument(
        "--publish",
        action="store_true",
        help="Retag and push each verified image to its canonical task tag.",
    )
    args = parser.parse_args()

    dataset = args.dataset.resolve()
    tasks = [
        line.strip()
        for line in args.tasks_file.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    if not tasks or len(tasks) != len(set(tasks)):
        raise SystemExit("tasks file must contain unique task names")

    rows = []
    dockerfile = {
        "rust": RUST_DOCKERFILE,
        "java": JAVA_DOCKERFILE,
        "go": GO_DOCKERFILE,
    }[args.toolchain]
    for task in tasks:
        canonical = task_image(dataset, task)
        source = source_digest(canonical)
        staging = f"{args.staging_repository}:{task}"
        run(
            [
                "docker",
                "build",
                "--build-arg",
                f"BASE_IMAGE={source}",
                "--tag",
                staging,
                "-",
            ],
            input_text=dockerfile,
        )
        verify(staging, args.toolchain)
        staging_id = run(
            [
                "docker",
                "image",
                "inspect",
                staging,
                "--format",
                "{{.Id}}",
            ]
        )
        published_digest = ""
        if args.publish:
            run(["docker", "tag", staging, canonical])
            run(["docker", "push", canonical])
            verify(canonical, args.toolchain)
            published_digest = source_digest(canonical)
        rows.append(
            {
                "task": task,
                "canonical_image": canonical,
                "source_digest": source,
                "staging_image": staging,
                "staging_image_id": staging_id,
                "published": args.publish,
                "published_digest": published_digest,
            }
        )
        print(f"verified {task}: {staging}")

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "repair": (
            "Expose the installed toolchain through login-shell-stable "
            "environment variables and /usr/local/bin entry points."
        ),
        "toolchain": args.toolchain,
        "published": args.publish,
        "images": rows,
    }
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {args.manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
