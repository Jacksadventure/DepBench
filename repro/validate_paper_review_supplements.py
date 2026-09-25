#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""Validate published supplementary data and recompute two-model agreement."""

from __future__ import annotations

import csv
import gzip
import hashlib
import json
import re
from collections import Counter
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / "paper_review"
ANALYSIS = REVIEW / "analysis"
STUDY = ANALYSIS / "opencode_gemini_dual_annotation"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def csv_rows(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def kappa(pairs: list[tuple[str, str]]) -> tuple[float, float]:
    n = len(pairs)
    require(n > 0, "no paired labels")
    first, second = Counter(a for a, _ in pairs), Counter(b for _, b in pairs)
    observed = Fraction(sum(a == b for a, b in pairs), n)
    chance = Fraction(sum(first[k] * second[k] for k in first.keys() | second.keys()), n * n)
    require(chance < 1, "kappa undefined for constant labels")
    return float(observed), float((observed - chance) / (1 - chance))


def parse_response(text: str) -> dict:
    return json.loads(re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip()))


def quote_present(quote: str, source: str) -> bool:
    escapes = {"n": "\n", "r": "\r", "t": "\t", '"': '"', "/": "/"}
    decoded = re.sub(r'\\([nrt"/])', lambda match: escapes[match.group(1)], source)
    query = " ".join(quote.split())
    return bool(query) and (query in " ".join(source.split()) or query in " ".join(decoded.split()))


def main() -> None:
    publication = json.loads((ANALYSIS / "supplement_manifest.json").read_text())
    for record in publication["files"]:
        path = ANALYSIS / record["path"]
        require(path.is_file(), f"missing published file: {record['path']}")
        require(hashlib.sha256(path.read_bytes()).hexdigest() == record["published_sha256"],
                f"published checksum mismatch: {record['path']}")
    outcomes = csv_rows(REVIEW / "results/final_per_task_outcomes.csv")
    expected = {
        (row["task"], row["final_trial"])
        for row in outcomes
        if row["configuration"] == "gemini35flash__opencode" and row["final_reward"] != "1.0"
    }
    manifest = json.loads((STUDY / "manifest.json").read_text())
    require(len(manifest) == len({r["id"] for r in manifest}) == 150, "invalid annotation manifest")
    require({(r["task"], r["trial"]) for r in manifest} == expected, "annotation/result cohort mismatch")
    with gzip.open(STUDY / "evidence_packets.jsonl.gz", "rt", encoding="utf-8") as handle:
        evidence_rows = [json.loads(line) for line in handle]
    packets = {row["id"]: row["packet"] for row in evidence_rows}
    require(len(packets) == len(evidence_rows) == 150, "duplicate or missing evidence packets")
    protocol = json.loads((STUDY / "protocol.json").read_text())
    require(hashlib.sha256(protocol["rubric"].encode()).hexdigest() == protocol["rubric_sha256"],
            "rubric hash mismatch")
    require(protocol["models"]["A"]["model"] != protocol["models"]["B"]["model"],
            "annotators must use distinct models")
    pairs, dispositions, additional_evidence = [], Counter(), Counter()
    for item in manifest:
        packet = packets[item["id"]]
        require(
            hashlib.sha256(json.dumps(packet, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
            == item["packet_sha256"], f"evidence hash mismatch: {item['id']}",
        )
        meta = json.loads(packet["metadata"])
        require(not {"prior_annotations", "prior_annotations_for_adjudication", "category", "ai_review"} & meta.keys(),
                "prior labels leaked into a blind packet")
        categories = []
        for coder in ("A", "B"):
            row = json.loads((STUDY / "labels" / coder / f"{item['id']}.json").read_text())
            require((row["task"], row["trial"]) == (item["task"], item["trial"]), "label identity mismatch")
            require(row["packet_sha256"] == item["packet_sha256"], "label evidence mismatch")
            require(row["rubric_sha256"] == protocol["rubric_sha256"], "rubric mismatch")
            require(row["requested_model"] == protocol["models"][coder]["model"], "model mismatch")
            require(not row["other_labels_visible"] and not row["human_review_completed"],
                    "annotation provenance is not independently automated")
            require(row["category"] in protocol["label_taxonomy"], "unknown category")
            raw = json.loads((STUDY / "attempts" / coder / f"{item['id']}-{row['response_id']}.json").read_text())
            original = parse_response(raw["text"])
            require(all(original[key] == row[key] for key in ("category", "rationale", "confidence")),
                    "category/rationale/confidence was modified before agreement")
            require(raw["packet_sha256"] == item["packet_sha256"]
                    and raw["rubric_sha256"] == protocol["rubric_sha256"],
                    "raw response evidence/rubric mismatch")
            require(len(row["evidence"]) > 0, "annotation has no evidence citations")
            for citation in row["evidence"]:
                require(citation["section"] in packet
                        and quote_present(citation["quote"], packet[citation["section"]]),
                        f"unsupported citation: {coder}/{item['id']}")
            categories.append(row["category"])
            additional_evidence[coder] += row["needs_more_evidence"]
        a, b = categories
        pairs.append((a, b))
        if "insufficient-evidence" in (a, b):
            dispositions["insufficient-evidence"] += 1
        elif a != b:
            dispositions["annotator-disagreement"] += 1
        else:
            dispositions[a] += 1
    observed, coefficient = kappa(pairs)
    summary = json.loads((STUDY / "summary.json").read_text())
    require(summary["valid_outputs"] == {"A": 150, "B": 150} and not summary["missing"], "incomplete annotation")
    require(dict(dispositions) == summary["consensus_table_counts"], "consensus counts differ")
    require(abs(observed - summary["agreement_all_labels"]["agreement"]) < 1e-12
            and abs(coefficient - summary["agreement_all_labels"]["kappa"]) < 1e-12,
            "agreement does not reproduce")
    require(dict(additional_evidence) == summary["additional_evidence_requested"],
            "additional-evidence counts differ")
    concrete = [pair for pair in pairs if "insufficient-evidence" not in pair]
    concrete_agreement, concrete_kappa = kappa(concrete)
    require(len(concrete) == summary["agreement_concrete_pairs"]["n"]
            and abs(concrete_agreement - summary["agreement_concrete_pairs"]["agreement"]) < 1e-12
            and abs(concrete_kappa - summary["agreement_concrete_pairs"]["kappa"]) < 1e-12,
            "concrete-label agreement does not reproduce")
    matrix = csv_rows(STUDY / "confusion_matrix.csv")
    counts = Counter(pairs)
    for row in matrix:
        a = row["A_category / B_category"]
        for b, count in row.items():
            if b != "A_category / B_category":
                require(int(count) == counts[a, b], "confusion matrix differs")
    paired = json.loads((STUDY / "paired_labels.json").read_text())
    require(len(paired) == 150 and [(r["A_category"], r["B_category"]) for r in paired] == pairs,
            "exported paired labels differ")

    rates = csv_rows(ANALYSIS / "rebuttal_supplements/rates.csv")
    published_rates = {
        f"{row['llm']}__{row['harness']}": row for row in csv_rows(REVIEW / "results/summary.csv")
    }
    require(len(rates) == 10, "unexpected supplementary result configurations")
    for row in rates:
        original = published_rates[row["configuration"]]
        require(int(row["passes"]) == int(original["pass"]) and int(row["tasks"]) == 203,
                "supplementary score does not match the published result")
        require(abs(float(row["rate"]) - int(row["passes"]) / 203) < 1e-12, "pass rate differs")
    runs = json.loads((ANALYSIS / "budget_audit/inputs/runs.json").read_text())
    require(len(runs) == len({(r["configuration"], r["task"], r["trial"]) for r in runs}) == 2030,
            "budget records do not cover the selected cohort")
    selected = {(r["configuration"], r["task"], r["final_trial"]) for r in outcomes}
    require({(r["configuration"], r["task"], r["trial"]) for r in runs} == selected,
            "budget trial identities differ")
    require(sum(r["exception"] == "AgentTimeoutError" for r in runs) == 233, "agent timeout count differs")
    require(sum(r["inner_verifier_timeout"] for r in runs) == 26, "verifier timeout count differs")
    print(f"Validated 150 independent pairs: agreement={observed:.6f}, kappa={coefficient:.6f}.")
    print("Supplementary scores, budgets, evidence hashes and selected-run identities match the review artifact.")


if __name__ == "__main__":
    main()
