#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""Run repository-level checks that can be automated before a public release."""

from __future__ import annotations

import base64
import csv
import gzip
import hashlib
import json
import re
import subprocess
import tarfile
from collections import Counter, defaultdict
from pathlib import Path, PurePosixPath


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
    "OpenAI-style key": re.compile(
        rb"\b(?:sk-proj|sk|rk)-[A-Za-z0-9_-]{20,}\b"
    ),
    "AWS access key": re.compile(rb"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b"),
}
PRIVATE_KEY_PATTERN = re.compile(
    rb"-----BEGIN (?:(?:RSA|EC|DSA|OPENSSH|ENCRYPTED) )?PRIVATE KEY-----"
)
KNOWN_EXAMPLE_AWS_KEY = b"AKIAI44QH8DHBEXAMPLE"
MAX_PUBLICATION_FILE_BYTES = 95 * 1024 * 1024


def release_files() -> list[Path]:
    command = ["git", "ls-files", "-co", "--exclude-standard"]
    names = subprocess.check_output(command, cwd=ROOT, text=True).splitlines()
    files = [ROOT / name for name in names if (ROOT / name).is_file()]
    tasks = ROOT / "dataset/tasks"
    if tasks.is_dir():
        files.extend(path for path in tasks.rglob("*") if path.is_file())
    return sorted(set(files))


def safe_archive_members(
    archive: tarfile.TarFile,
    *,
    relative: Path,
    errors: list[str],
) -> list[tarfile.TarInfo]:
    members = archive.getmembers()
    names = [member.name for member in members]
    if len(names) != len(set(names)):
        errors.append(f"{relative}: archive contains duplicate member names")
    safe = []
    for member in members:
        name = PurePosixPath(member.name)
        if name.is_absolute() or ".." in name.parts:
            errors.append(f"{relative}: unsafe archive member {member.name!r}")
            continue
        if not member.isfile():
            errors.append(
                f"{relative}: archive member is not a regular file: "
                f"{member.name!r}"
            )
            continue
        safe.append(member)
    return safe


def iter_payloads(path: Path, errors: list[str]):
    relative = path.relative_to(ROOT)
    if path.name.endswith(".tar.gz"):
        try:
            with tarfile.open(path, "r:gz") as archive:
                members = safe_archive_members(
                    archive, relative=relative, errors=errors
                )
                task_by_trial = {}
                for member in members:
                    if not member.name.endswith("/result.json"):
                        continue
                    extracted = archive.extractfile(member)
                    if extracted is None:
                        errors.append(
                            f"{relative}: cannot extract {member.name!r}"
                        )
                        continue
                    try:
                        result = json.loads(extracted.read())
                    except (UnicodeDecodeError, json.JSONDecodeError):
                        continue
                    task = str(result.get("task_name") or "").split("/")[-1]
                    if task:
                        task_by_trial[
                            member.name.removesuffix("/result.json")
                        ] = task
                for member in members:
                    extracted = archive.extractfile(member)
                    if extracted is None:
                        errors.append(
                            f"{relative}: cannot extract {member.name!r}"
                        )
                        continue
                    trial_root = next(
                        (
                            root
                            for root in task_by_trial
                            if member.name == root
                            or member.name.startswith(f"{root}/")
                        ),
                        "",
                    )
                    yield (
                        f"{relative}:{member.name}",
                        extracted.read(),
                        str(relative),
                        task_by_trial.get(trial_root, "job-bundle"),
                    )
        except (tarfile.TarError, OSError) as error:
            errors.append(f"{relative}: cannot unpack tar archive: {error}")
        return

    if path.suffix == ".gz":
        try:
            with gzip.open(path, "rb") as handle:
                for line_number, line in enumerate(handle, 1):
                    task = "compressed-artifact"
                    try:
                        row = json.loads(line)
                        task = str(row.get("task") or task)
                    except (UnicodeDecodeError, json.JSONDecodeError):
                        pass
                    yield (
                        f"{relative}:{line_number}",
                        line,
                        str(relative),
                        task,
                    )
        except (gzip.BadGzipFile, OSError, EOFError) as error:
            errors.append(f"{relative}: cannot unpack gzip stream: {error}")
        return

    task = "repository-file"
    if relative.parts[:2] == ("dataset", "tasks") and len(relative.parts) >= 3:
        task = relative.parts[2]
    yield str(relative), path.read_bytes(), str(relative), task


def evidence_fingerprint(rows: list[tuple[str, bytes]]) -> str:
    digest = hashlib.sha256()
    for label, payload in sorted(rows):
        digest.update(label.encode("utf-8"))
        digest.update(b"\0")
        digest.update(hashlib.sha256(payload).digest())
    return digest.hexdigest()


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
        "custom": 2,
    }
    if dict(category_tasks) != expected:
        errors.append(
            f"unexpected task license-category counts: {dict(category_tasks)}"
        )

    notice = (ROOT / "THIRD_PARTY_NOTICES.md").read_text(encoding="utf-8")
    for identifier in (
        "SSPL-1.0",
        "Elastic-2.0",
        "FSL-1.1-ALv2",
        "LicenseRef-Apache-2.0-with-MITRE-terms",
        "LicenseRef-MIT-with-GovTech-terms",
        "BUSL-1.1",
    ):
        if identifier not in notice:
            errors.append(f"third-party notice missing identifier: {identifier}")


def scan_content(errors: list[str], warnings: list[str]) -> None:
    private_key_counts: Counter[tuple[str, str]] = Counter()
    private_key_evidence: dict[
        tuple[str, str], list[tuple[str, bytes]]
    ] = defaultdict(list)
    scanned = 0
    for path in release_files():
        if path.resolve() == SELF:
            continue
        relative = path.relative_to(ROOT)
        if (
            relative.parts
            and relative.parts[0] == "jobs"
            and path.stat().st_size >= MAX_PUBLICATION_FILE_BYTES
        ):
            errors.append(
                f"{relative}: exceeds the 95 MiB publication limit"
            )
        for label, payload, artifact, task in iter_payloads(path, errors):
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

            count = len(PRIVATE_KEY_PATTERN.findall(payload))
            if count:
                key = (artifact, task)
                private_key_counts[key] += count
                private_key_evidence[key].append((label, payload))

    review_rows = list(
        csv.DictReader(
            (ROOT / "analysis/secret_scan_review_2026-07-23.csv").open(
                encoding="utf-8"
            )
        )
    )
    dataset_present = (ROOT / "dataset/tasks").is_dir()
    applicable_rows = [
        row
        for row in review_rows
        if dataset_present or not row["artifact"].startswith("dataset/")
    ]
    documented = {}
    for row in applicable_rows:
        key = (row["artifact"], row["task"])
        if key in documented:
            errors.append(f"duplicate private-key review row: {key}")
            continue
        documented[key] = row
        classification = row["classification"].strip().upper()
        disposition = row["disposition"].strip().upper()
        if classification == "UNREVIEWED" or disposition == "BLOCK_RELEASE":
            errors.append(
                f"{key}: private-key evidence has not been approved"
            )

    observed = {
        key: {
            "count": count,
            "evidence_sha256": evidence_fingerprint(
                private_key_evidence[key]
            ),
        }
        for key, count in private_key_counts.items()
    }
    documented_values = {
        key: {
            "count": int(row["private_key_headers"]),
            "evidence_sha256": row.get("evidence_sha256", ""),
        }
        for key, row in documented.items()
    }
    if observed != documented_values:
        errors.append(
            "private-key evidence differs from the reviewed inventory: "
            f"missing={sorted(set(observed) - set(documented_values))} "
            f"extra={sorted(set(documented_values) - set(observed))} "
            f"changed={sorted(key for key in set(observed) & set(documented_values) if observed[key] != documented_values[key])}"
        )

    private_key_hits = sum(private_key_counts.values())
    if private_key_hits:
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
