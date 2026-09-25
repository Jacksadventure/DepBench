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


def canonical_hash(value: object) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def adjudicated_categories(paired: list[dict], decisions: dict[str, dict]) -> dict[str, str]:
    expected = {row["id"] for row in paired if row["disposition"] == "annotator-disagreement"}
    require(set(decisions) == expected, "adjudications must cover exactly the original disagreements")
    return {
        row["id"]: decisions[row["id"]]["category"] if row["id"] in decisions else row["disposition"]
        for row in paired
    }


def validate_adjudication(packets: dict, paired: list[dict], original_summary: dict) -> None:
    study = ANALYSIS / "opencode_gemini_adjudication"
    protocol = json.loads((study / "protocol.json").read_text())
    require(protocol["judge_model"] == "gpt-6-astra" and protocol["adjudication_cases"] == 69,
            "unexpected third-model protocol")
    require(protocol["other_labels_visible"] and not protocol["judge_is_an_independent_primary_annotator"]
            and not protocol["human_review_claimed"], "misstated adjudication provenance")
    require(hashlib.sha256(protocol["rubric"].encode()).hexdigest() == protocol["rubric_sha256"],
            "adjudication rubric hash mismatch")
    for relative, digest in protocol["original_files_sha256"].items():
        require(hashlib.sha256((STUDY / relative).read_bytes()).hexdigest() == digest,
                f"original independent annotation changed: {relative}")
    manifest = json.loads((study / "manifest.json").read_text())
    assignments = json.loads((study / "assignments.json").read_text())
    executions = json.loads((study / "executions.json").read_text())
    assigned = [identity for batch in assignments for identity in batch["ids"]]
    expected = {row["id"] for row in paired if row["disposition"] == "annotator-disagreement"}
    require(len(assigned) == len(set(assigned)) == len(manifest) == 69
            and set(assigned) == expected == {row["id"] for row in manifest},
            "adjudication selection/assignment differs from the 69 disagreements")
    batch_for = {identity: batch["batch"] for batch in assignments for identity in batch["ids"]}
    require({row["batch"] for row in assignments} == set(executions), "execution batches differ")
    require(len({row["agent_id"] for row in executions.values()}) == 3
            and all(row["requested_model"] == row["reported_model"] == "gpt-6-astra"
                    and row["status"] == "completed" for row in executions.values()),
            "missing distinct GPT-6 batch invocation records")
    taxonomy = json.loads((STUDY / "protocol.json").read_text())["label_taxonomy"]
    allowed_fields = {
        "category", "confidence", "rationale", "evidence", "alternatives",
        "needs_more_evidence", "missing_evidence",
    }
    decisions = {}
    for item in manifest:
        identity = item["id"]
        packet = packets[identity]
        inputs = json.loads((study / "inputs" / f"{identity}.json").read_text())
        require(canonical_hash(packet) == item["packet_sha256"], "adjudication evidence changed")
        require(canonical_hash({"packet": packet, "annotations": inputs["annotations"]})
                == item["judge_input_sha256"], "adjudicator input hash mismatch")
        for coder in ("A", "B"):
            prior = json.loads((STUDY / "labels" / coder / f"{identity}.json").read_text())
            require(inputs["annotations"][coder] == {key: prior[key] for key in allowed_fields},
                    "judge did not receive the declared blinded prior label")
            require(canonical_hash(prior) == item["original_label_sha256"][coder],
                    "original label hash mismatch")
        path = study / "raw" / f"{identity}.json"
        raw = json.loads(path.read_text())
        decision = json.loads((study / "decisions" / f"{identity}.json").read_text())
        require(decision["id"] == identity and raw["id"] == identity, "judge case identity differs")
        require(all(decision[key] == item[key] for key in item), "judge case provenance differs")
        require(decision["raw_sha256"] == hashlib.sha256(path.read_bytes()).hexdigest(),
                "raw judge decision hash mismatch")
        require(all(raw[key] == decision[key] for key in ("category", "confidence", "rationale")),
                "judge decision was altered during citation recovery")
        require(decision["rubric_sha256"] == protocol["rubric_sha256"]
                and decision["judge_model"] == "gpt-6-astra"
                and decision["batch"] == batch_for[identity]
                and decision["agent_id"] == executions[batch_for[identity]]["agent_id"]
                and decision["other_labels_visible"] and not decision["human_review_completed"],
                "judge execution provenance differs")
        require(decision["category"] in taxonomy, "judge chose an unknown category")
        require(bool(decision["evidence"]), "judge decision has no evidence")
        for citation in decision["evidence"]:
            require(citation["section"] in packet
                    and quote_present(citation["quote"], packet[citation["section"]]),
                    f"unsupported judge citation: {identity}")
        if decision["category"] == "insufficient-evidence":
            require(decision["needs_more_evidence"] and bool(decision["missing_evidence"].strip()),
                    "judge abstention does not identify missing evidence")
        decisions[identity] = decision
    expected_final = adjudicated_categories(paired, decisions)
    final = json.loads((study / "final_labels.json").read_text())
    require(len(final) == len({row["id"] for row in final}) == 150
            and {row["id"]: row["final_category"] for row in final} == expected_final,
            "final labels do not preserve consensus, abstention and adjudicated cases")
    for row in final:
        decision = decisions.get(row["id"])
        require(row["judge_confidence"] == (decision["confidence"] if decision else None)
                and row["judge_needs_more_evidence"] == (decision["needs_more_evidence"] if decision else None),
                "exported judge uncertainty differs")
    counts = Counter(expected_final.values())
    summary = json.loads((study / "summary.json").read_text())
    require(summary["adjudicated"] == 69 and summary["selected_nonpasses"] == 150
            and summary["original_consensus_preserved"] == 80
            and summary["original_insufficient_evidence_preserved"] == 1
            and summary["final_category_counts"] == dict(counts), "final category totals differ")
    require(summary["judge_confidence_counts"] == dict(Counter(row["confidence"] for row in decisions.values()))
            and summary["judge_additional_evidence_requested"]
            == sum(row["needs_more_evidence"] for row in decisions.values()),
            "judge uncertainty summary differs")
    require(summary["pre_adjudication_agreement"] == original_summary["agreement_all_labels"]
            and not summary["independent_agreement_recomputed_after_adjudication"]
            and not summary["human_review_completed"] and not summary["benchmark_rewards_changed"],
            "adjudication was incorrectly treated as independent agreement or a score change")
    original_table = {row["category"]: row for row in csv_rows(STUDY / "table5_counts.csv")}
    table = csv_rows(study / "table5_counts.csv")
    require(len(table) == 10 and len({row["category"] for row in table}) == 10,
            "unexpected final Table 5 categories")
    for row in table:
        category = row["category"]
        require(category in original_table and category != "annotator-disagreement", "invalid final table row")
        for config, number in row.items():
            if config == "category":
                continue
            expected_count = counts[category] if config == "gemini35flash__opencode" else int(original_table[category][config])
            require(int(number) == expected_count, "final Table 5 count differs")
    print("Validated 69 GPT-6 adjudications; 80 consensus cases and one original abstention preserved.")


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
    if "adjudication" in publication:
        require(publication["adjudication"]["cases"] == 69
                and publication["adjudication"]["model"] == "gpt-6-astra",
                "published adjudication descriptor differs")
        validate_adjudication(packets, paired, summary)

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
