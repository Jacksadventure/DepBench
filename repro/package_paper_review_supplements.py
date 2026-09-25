#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""Package saved review analyses; never call models or rerun benchmark tasks."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "paper_review/analysis"
STUDIES = ("opencode_gemini_dual_annotation", "rebuttal_supplements", "budget_audit")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def omit_reasoning(value):
    if isinstance(value, dict):
        return {key: omit_reasoning(item) for key, item in value.items() if key != "reasoning_content"}
    if isinstance(value, list):
        return [omit_reasoning(item) for item in value]
    return value


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-analysis", type=Path, required=True)
    parser.add_argument("--packets", type=Path, required=True)
    parser.add_argument("--strip-local-prefix", required=True)
    args = parser.parse_args()
    prefix = args.strip_local_prefix.rstrip("/") + "/"
    if prefix == "/":
        parser.error("a specific host-local prefix is required")
    inventory = []
    for study in STUDIES:
        source = args.source_analysis / study
        if not source.is_dir():
            raise SystemExit(f"missing source study: {study}")
        for path in sorted(source.rglob("*")):
            if (not path.is_file() or path.name == "README.md"
                    or path.suffix not in {".json", ".csv", ".jsonl", ".md"}):
                continue
            relative = Path(study) / path.relative_to(source)
            original = path.read_bytes()
            text = original.decode("utf-8")
            changes = []
            if path.suffix == ".json" and "reasoning_content" in text:
                value = json.loads(text)
                cleaned = omit_reasoning(value)
                if cleaned != value:
                    changes.append("omit_unneeded_reasoning_field")
                    text = json.dumps(cleaned, ensure_ascii=False, indent=2) + "\n"
            if prefix in text:
                text = text.replace(prefix, "local_sources/")
                changes.append("replace_host_local_path_prefix")
            published = text.encode("utf-8")
            destination = TARGET / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(published)
            inventory.append({
                "path": str(relative), "source_sha256": sha256(original),
                "published_sha256": sha256(published), "transformations": changes,
            })

    study = TARGET / "opencode_gemini_dual_annotation"
    manifest = json.loads((study / "manifest.json").read_text())
    packets = []
    for item in manifest:
        packet = json.loads((args.packets / f"{item['id']}.json").read_text())
        digest = sha256(json.dumps(packet, ensure_ascii=False, sort_keys=True).encode())
        if digest != item["packet_sha256"]:
            raise SystemExit(f"frozen evidence hash mismatch: {item['id']}")
        packets.append(json.dumps({
            "id": item["id"], "task": item["task"], "trial": item["trial"], "packet": packet,
        }, ensure_ascii=False, sort_keys=True) + "\n")
    evidence_path = study / "evidence_packets.jsonl.gz"
    evidence_path.write_bytes(gzip.compress("".join(packets).encode(), mtime=0))
    inventory.append({
        "path": str(evidence_path.relative_to(TARGET)),
        "published_sha256": sha256(evidence_path.read_bytes()),
        "transformations": ["lossless_deterministic_gzip_of_frozen_packets"],
    })
    publication = {
        "purpose": "paper-review supplementary analyses",
        "task_cohort": 203, "selected_runs": 2030,
        "dual_annotation_configuration": "gemini35flash__opencode",
        "dual_annotation_cases": 150, "new_benchmark_runs": False,
        "human_review_claimed": False,
        "files": inventory,
    }
    (TARGET / "supplement_manifest.json").write_text(json.dumps(publication, indent=2) + "\n")
    print(f"Packaged {len(inventory)} analysis files and 150 frozen evidence packets.")


if __name__ == "__main__":
    main()
