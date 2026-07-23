#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""Remove credential-like and internal-only strings from trajectory exports."""

from __future__ import annotations

import base64
import csv
import gzip
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
INVENTORY_PATH = ROOT / "analysis/release_redactions_2026-07-23.csv"
INTERNAL_MARKERS = tuple(
    base64.b64decode(value).decode("ascii")
    for value in (
        "L0RhdGEyLw==",
        "di16aWppYW5sdW8=",
        "Q09ERVhfTUFFU1RSTw==",
        "bXNyNGFnZW50",
    )
)
SECRET_PATTERNS = (
    re.compile(r"(?:github_pat_[A-Za-z0-9_]{20,}|gh[pousr]_[A-Za-z0-9]{30,})"),
    re.compile(r"\b(?:sk|rk)-[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
)
KNOWN_EXAMPLE_AWS_KEY = "AKIAI44QH8DHBEXAMPLE"
REPLACEMENT = "[REDACTED: credential-like or internal-only content removed]"


def reason_for(value: str) -> str | None:
    if any(marker in value for marker in INTERNAL_MARKERS):
        return "unrelated internal session metadata"
    for pattern in SECRET_PATTERNS:
        match = pattern.search(value)
        if not match:
            continue
        if match.group(0) == KNOWN_EXAMPLE_AWS_KEY:
            continue
        return "credential-like content"
    return None


def redact(
    value: Any,
    *,
    path: str,
    findings: list[tuple[str, str]],
) -> Any:
    if isinstance(value, dict):
        return {
            key: redact(
                item,
                path=f"{path}.{key}" if path else key,
                findings=findings,
            )
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [
            redact(item, path=f"{path}[{index}]", findings=findings)
            for index, item in enumerate(value)
        ]
    if isinstance(value, str):
        reason = reason_for(value)
        if reason:
            findings.append((path, reason))
            return REPLACEMENT
    return value


def read_inventory() -> list[dict[str, str]]:
    if not INVENTORY_PATH.exists():
        return []
    return list(csv.DictReader(INVENTORY_PATH.open(encoding="utf-8")))


def main() -> int:
    inventory = read_inventory()
    known = {
        (row["artifact"], row["task"], row["json_path"], row["reason"])
        for row in inventory
    }
    changed_rows = 0

    for trajectory_path in sorted((ROOT / "trajectories").glob("*.jsonl.gz")):
        rows = []
        changed = False
        with gzip.open(trajectory_path, "rt", encoding="utf-8") as handle:
            for line in handle:
                row = json.loads(line)
                findings: list[tuple[str, str]] = []
                redacted = redact(row, path="", findings=findings)
                if findings:
                    changed = True
                    changed_rows += 1
                    artifact = str(trajectory_path.relative_to(ROOT))
                    for json_path, reason in findings:
                        key = (artifact, row["task"], json_path, reason)
                        if key in known:
                            continue
                        inventory.append(
                            {
                                "artifact": artifact,
                                "task": row["task"],
                                "json_path": json_path,
                                "action": "replaced message",
                                "reason": reason,
                            }
                        )
                        known.add(key)
                rows.append(redacted)

        if changed:
            with gzip.open(trajectory_path, "wt", encoding="utf-8") as handle:
                for row in rows:
                    handle.write(
                        json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n"
                    )

    inventory.sort(
        key=lambda row: (row["artifact"], row["task"], row["json_path"])
    )
    with INVENTORY_PATH.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["artifact", "task", "json_path", "action", "reason"],
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(inventory)
    print(f"redacted {changed_rows} trajectory row(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
