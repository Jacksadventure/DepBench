#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""Refresh the reviewed inventory of public private-key fixture headers."""

from __future__ import annotations

import csv
import gzip
import hashlib
import json
import re
import tarfile
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "analysis/secret_scan_review_2026-07-23.csv"
PRIVATE_KEY_PATTERN = re.compile(
    rb"-----BEGIN (?:(?:RSA|EC|DSA|OPENSSH|ENCRYPTED) )?PRIVATE KEY-----"
)


def existing_metadata() -> dict[tuple[str, str], tuple[str, str, str]]:
    if not OUTPUT.exists():
        return {}
    return {
        (row["artifact"], row["task"]): (
            row["classification"],
            row["disposition"],
            row.get("evidence_sha256", ""),
        )
        for row in csv.DictReader(OUTPUT.open(encoding="utf-8"))
    }


def evidence_fingerprint(rows: list[tuple[str, bytes]]) -> str:
    digest = hashlib.sha256()
    for label, payload in sorted(rows):
        digest.update(label.encode("utf-8"))
        digest.update(b"\0")
        digest.update(hashlib.sha256(payload).digest())
    return digest.hexdigest()


def main() -> int:
    metadata = existing_metadata()
    counts: Counter[tuple[str, str]] = Counter()
    evidence: dict[tuple[str, str], list[tuple[str, bytes]]] = defaultdict(list)

    for path in sorted((ROOT / "dataset/tasks").glob("**/*")):
        if not path.is_file():
            continue
        payload = path.read_bytes()
        count = len(PRIVATE_KEY_PATTERN.findall(payload))
        if count:
            relative = path.relative_to(ROOT)
            task = relative.parts[2]
            key = (str(relative), task)
            counts[key] += count
            evidence[key].append((str(relative), payload))

    for path in sorted((ROOT / "trajectories").glob("*.jsonl.gz")):
        artifact = str(path.relative_to(ROOT))
        with gzip.open(path, "rb") as handle:
            for line_number, line in enumerate(handle, 1):
                count = len(PRIVATE_KEY_PATTERN.findall(line))
                if not count:
                    continue
                task = json.loads(line)["task"]
                key = (artifact, task)
                counts[key] += count
                evidence[key].append((f"{artifact}:{line_number}", line))

    for path in sorted((ROOT / "jobs").glob("**/*.tar.gz")):
        artifact = str(path.relative_to(ROOT))
        with tarfile.open(path, "r:gz") as archive:
            members = [
                member for member in archive.getmembers() if member.isfile()
            ]
            task_by_trial = {}
            for member in members:
                if not member.name.endswith("/result.json"):
                    continue
                extracted = archive.extractfile(member)
                if extracted is None:
                    continue
                result = json.loads(extracted.read())
                task = str(result.get("task_name") or "").split("/")[-1]
                if task:
                    task_by_trial[member.name.removesuffix("/result.json")] = task

            for member in members:
                extracted = archive.extractfile(member)
                if extracted is None:
                    continue
                payload = extracted.read()
                count = len(PRIVATE_KEY_PATTERN.findall(payload))
                if not count:
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
                task = task_by_trial.get(trial_root, "job-bundle")
                key = (artifact, task)
                counts[key] += count
                evidence[key].append(
                    (f"{artifact}:{member.name}", payload)
                )

    rows = []
    for (artifact, task), count in sorted(counts.items()):
        fingerprint = evidence_fingerprint(evidence[(artifact, task)])
        previous = metadata.get((artifact, task))
        if previous and (not previous[2] or previous[2] == fingerprint):
            classification, disposition, _ = previous
        else:
            classification = "UNREVIEWED"
            disposition = "BLOCK_RELEASE"
        rows.append(
            {
                "artifact": artifact,
                "task": task,
                "private_key_headers": count,
                "evidence_sha256": fingerprint,
                "classification": classification,
                "disposition": disposition,
            }
        )

    with OUTPUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=list(rows[0]), lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)
    print(
        f"recorded {sum(counts.values())} private-key fixture headers "
        f"across {len(rows)} artifact/task rows"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
