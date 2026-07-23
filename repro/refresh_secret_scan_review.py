#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""Refresh the reviewed inventory of public private-key fixture headers."""

from __future__ import annotations

import csv
import gzip
import json
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "analysis/secret_scan_review_2026-07-23.csv"
PRIVATE_KEY_PATTERN = re.compile(
    rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"
)


def existing_metadata() -> dict[tuple[str, str], tuple[str, str]]:
    if not OUTPUT.exists():
        return {}
    return {
        (row["artifact"], row["task"]): (
            row["classification"],
            row["disposition"],
        )
        for row in csv.DictReader(OUTPUT.open(encoding="utf-8"))
    }


def main() -> int:
    metadata = existing_metadata()
    counts: Counter[tuple[str, str]] = Counter()

    for path in sorted((ROOT / "dataset/tasks").glob("**/*")):
        if not path.is_file():
            continue
        count = len(PRIVATE_KEY_PATTERN.findall(path.read_bytes()))
        if count:
            relative = path.relative_to(ROOT)
            task = relative.parts[2]
            counts[(str(relative), task)] += count

    for path in sorted((ROOT / "trajectories").glob("*.jsonl.gz")):
        artifact = str(path.relative_to(ROOT))
        with gzip.open(path, "rb") as handle:
            for line in handle:
                count = len(PRIVATE_KEY_PATTERN.findall(line))
                if not count:
                    continue
                task = json.loads(line)["task"]
                counts[(artifact, task)] += count

    rows = []
    for (artifact, task), count in sorted(counts.items()):
        classification, disposition = metadata.get(
            (artifact, task),
            (
                "public upstream test fixture",
                "manual scanner suppression or artifact redaction required",
            ),
        )
        rows.append(
            {
                "artifact": artifact,
                "task": task,
                "private_key_headers": count,
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
