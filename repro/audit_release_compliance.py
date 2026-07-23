#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""Run repository-level checks that can be automated before a public release."""

from __future__ import annotations

import base64
import csv
import gzip
import re
import subprocess
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SELF = Path(__file__).resolve()

REQUIRED_FILES = (
    "README.md",
    "LICENSE.txt",
    "NOTICE.txt",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "CODE_OF_CONDUCT.md",
    "SUPPORT.md",
    "THIRD_PARTY_NOTICES.md",
    "OPEN_SOURCE_RELEASE_CHECKLIST.md",
)
REQUIRED_README_SECTIONS = (
    "## Licensing and third-party content",
    "## Data, privacy, and network notice",
    "## Trademarks",
)
SOURCE_GLOBS = ("setup.py", "custom_agents/*.py", "repro/*.py", "repro/*.sh")
HEADER = (
    "Copyright (c) Microsoft Corporation.",
    "Licensed under the MIT License.",
)

INTERNAL_MARKERS = tuple(
    base64.b64decode(value).decode("ascii")
    for value in (
        "L0RhdGEyLw==",
        "di16aWppYW5sdW8=",
        "Q09ERVhfTUFFU1RSTw==",
        "bXNyNGFnZW50",
    )
)
SECRET_PATTERNS = {
    "GitHub token": re.compile(
        rb"(?:github_pat_[A-Za-z0-9_]{20,}|gh[pousr]_[A-Za-z0-9]{30,})"
    ),
    "OpenAI-style key": re.compile(rb"\b(?:sk|rk)-[A-Za-z0-9]{20,}\b"),
    "AWS access key": re.compile(rb"\bAKIA[0-9A-Z]{16}\b"),
}
PRIVATE_KEY_PATTERN = re.compile(
    rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"
)
KNOWN_EXAMPLE_AWS_KEY = b"AKIAI44QH8DHBEXAMPLE"


def release_files() -> list[Path]:
    command = ["git", "ls-files", "-co", "--exclude-standard"]
    names = subprocess.check_output(command, cwd=ROOT, text=True).splitlines()
    files = [ROOT / name for name in names if (ROOT / name).is_file()]
    tasks = ROOT / "dataset/tasks"
    if tasks.is_dir():
        files.extend(path for path in tasks.rglob("*") if path.is_file())
    return sorted(set(files))


def iter_payloads(path: Path):
    relative = path.relative_to(ROOT)
    if path.suffix == ".gz":
        try:
            with gzip.open(path, "rb") as handle:
                for line_number, line in enumerate(handle, 1):
                    yield f"{relative}:{line_number}", line
        except (gzip.BadGzipFile, OSError):
            yield str(relative), path.read_bytes()
        return

    yield str(relative), path.read_bytes()


def check_governance(errors: list[str]) -> None:
    for name in REQUIRED_FILES:
        if not (ROOT / name).is_file():
            errors.append(f"missing required release file: {name}")

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for section in REQUIRED_README_SECTIONS:
        if section not in readme:
            errors.append(f"README missing required section: {section}")


def check_source_headers(errors: list[str]) -> None:
    sources: set[Path] = set()
    for pattern in SOURCE_GLOBS:
        sources.update(ROOT.glob(pattern))
    for path in sorted(sources):
        text = path.read_text(encoding="utf-8")
        first_lines = "\n".join(text.splitlines()[:8])
        for required in HEADER:
            if required not in first_lines:
                errors.append(
                    f"{path.relative_to(ROOT)} missing source header: {required}"
                )


def check_license_inventory(errors: list[str]) -> None:
    path = ROOT / "analysis/repository_metadata.csv"
    rows = list(csv.DictReader(path.open(encoding="utf-8")))
    category_tasks = Counter()
    for row in rows:
        category_tasks[row["license_category"]] += int(row["task_count"])

    expected = {
        "open_source": 192,
        "source_available": 7,
        "custom": 3,
        "not_declared": 1,
    }
    if dict(category_tasks) != expected:
        errors.append(
            f"unexpected task license-category counts: {dict(category_tasks)}"
        )

    notice = (ROOT / "THIRD_PARTY_NOTICES.md").read_text(encoding="utf-8")
    for identifier in (
        "SSPL-1.0",
        "LicenseRef-Databricks",
        "Elastic-2.0",
        "FSL-1.1-ALv2",
        "LicenseRef-Apache-2.0-with-MITRE-terms",
        "NOASSERTION",
        "LicenseRef-MIT-with-GovTech-terms",
        "BUSL-1.1",
    ):
        if identifier not in notice:
            errors.append(f"third-party notice missing identifier: {identifier}")


def scan_content(errors: list[str], warnings: list[str]) -> None:
    private_key_hits = 0
    scanned = 0
    for path in release_files():
        if path.resolve() == SELF:
            continue
        for label, payload in iter_payloads(path):
            scanned += len(payload)
            text = payload.decode("utf-8", errors="ignore")
            for marker in INTERNAL_MARKERS:
                if marker in text:
                    errors.append(f"{label}: contains internal marker {marker!r}")

            for name, pattern in SECRET_PATTERNS.items():
                for match in pattern.findall(payload):
                    if name == "AWS access key" and match == KNOWN_EXAMPLE_AWS_KEY:
                        continue
                    errors.append(f"{label}: possible {name}")

            private_key_hits += len(PRIVATE_KEY_PATTERN.findall(payload))

    if private_key_hits:
        review_rows = list(
            csv.DictReader(
                (ROOT / "analysis/secret_scan_review_2026-07-23.csv").open(
                    encoding="utf-8"
                )
            )
        )
        dataset_present = (ROOT / "dataset/tasks").is_dir()
        documented_hits = sum(
            int(row["private_key_headers"])
            for row in review_rows
            if dataset_present or not row["artifact"].startswith("dataset/")
        )
        if private_key_hits != documented_hits:
            errors.append(
                "private-key fixture count differs from the reviewed inventory: "
                f"observed={private_key_hits} documented={documented_hits}"
            )
        warnings.append(
            f"{private_key_hits} private-key header(s) found in public upstream "
            "test fixtures; obtain an approved scanner suppression or remove "
            "the affected artifacts without changing benchmark semantics; see "
            "analysis/secret_scan_review_2026-07-23.csv"
        )
    print(f"Scanned {scanned:,} uncompressed bytes.")


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []

    check_governance(errors)
    check_source_headers(errors)
    check_license_inventory(errors)
    scan_content(errors, warnings)

    for warning in sorted(set(warnings)):
        print(f"WARNING: {warning}")
    if errors:
        for error in sorted(set(errors)):
            print(f"ERROR: {error}")
        print(f"Release compliance audit failed with {len(set(errors))} error(s).")
        return 1

    print("Repository-level release compliance audit passed.")
    print(
        "External Open Source Portal, CELA, Open Data, privacy, SDL, RAI, "
        "trademark, and supply-chain approvals remain owner responsibilities."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
