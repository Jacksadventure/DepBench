#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import asyncio
import json
import os
import tempfile
import unittest
from collections import Counter
from pathlib import Path
from unittest.mock import AsyncMock, patch

import httpx

from run_multilabel_annotation import (
    EVIDENCE_FIELDS, MODELS, RUBRIC, TAXONOMY, TRANSPORTS, RequestGate, Study, digest,
    model_matches, parse_copilot_response, read_json, signature, validate_label, write_json,
    retry_after_seconds,
)


class MultilabelTests(unittest.TestCase):
    def setUp(self):
        self.packet = dict.fromkeys(EVIDENCE_FIELDS, "AgentTimeoutError: time limit exceeded")

    def annotation(self, *categories):
        return {
            "labels": [{
                "category": category, "confidence": "high", "rationale": "Observed cause",
                "evidence": [{"source": "run_metadata", "quote": "time limit exceeded"}],
            } for category in categories],
            "insufficient_evidence": not categories,
            "missing_evidence": "" if categories else "Missing observed behavior",
        }

    def test_multiple_causes_and_order_independent_comparison(self):
        a = self.annotation("execution-timeout", "code-adaptation-error")
        b = self.annotation("code-adaptation-error", "execution-timeout")
        self.assertEqual(validate_label(a, self.packet), a)
        self.assertEqual(signature(a), signature(b))
        self.assertNotEqual(signature(a), signature(self.annotation("execution-timeout")))

    def test_old_labels_and_duplicates_are_rejected(self):
        for categories in [
            ("wrong-root-cause",), ("wrong-semantic-output",), ("gave-up-or-budget",),
            ("execution-timeout", "execution-timeout"),
        ]:
            with self.subTest(categories=categories), self.assertRaises(ValueError):
                validate_label(self.annotation(*categories), self.packet)

    def test_abstention_must_be_explicit_and_exclusive(self):
        self.assertEqual(validate_label(self.annotation(), self.packet), self.annotation())
        for value in [
            {**self.annotation(), "insufficient_evidence": False},
            {**self.annotation(), "missing_evidence": ""},
            {**self.annotation("execution-timeout"), "insufficient_evidence": True},
        ]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                validate_label(value, self.packet)

    def test_invented_or_missing_citations_are_rejected(self):
        for citation in [
            {"source": "trajectory", "quote": "invented error"},
            {"source": "annotation_A", "quote": "time limit exceeded"},
            {"source": "run_metadata", "quote": ""},
        ]:
            value = self.annotation("execution-timeout")
            value["labels"][0]["evidence"] = [citation]
            with self.subTest(citation=citation), self.assertRaises(ValueError):
                validate_label(value, self.packet)
        value["labels"][0]["evidence"] = []
        with self.assertRaises(ValueError):
            validate_label(value, self.packet)

    def test_gateway_model_date_format_does_not_allow_model_substitution(self):
        self.assertTrue(model_matches("cloudgpt/gpt-6-astra-20260903", "gpt-6-astra-2026-09-03"))
        self.assertFalse(model_matches("cloudgpt/gpt-6-astra-20260903", "gpt-6.1-sol-20260929"))
        self.assertFalse(model_matches("cloudgpt/gpt-6-astra-20260903", ""))

    def test_copilot_response_must_verify_tools_disabled_and_exact_model(self):
        events = [
            {"type": "model.call_start", "data": {"model": "grok-4.7"}},
            {"type": "assistant.message", "data": {
                "model": "grok-4.7", "content": '{"ok":true}', "toolRequests": [],
            }},
            {"type": "session.usage_checkpoint", "data": {
                "promptCacheBreakState": [{"models": {"grok-4.7": {"tool_count": 0}}}],
            }},
            {"type": "result", "exitCode": 0, "sessionId": "test"},
        ]
        render = lambda rows: "\n".join(json.dumps(row) for row in rows)
        self.assertEqual(parse_copilot_response(render(events))["text"], '{"ok":true}')
        with self.assertRaises(ValueError):
            parse_copilot_response(render(events[:2] + events[3:]))
        events[0]["data"]["model"] = "auto"
        with self.assertRaises(ValueError):
            parse_copilot_response(render(events))
        events[0]["data"]["model"] = "grok-4.7"
        events[2]["data"]["promptCacheBreakState"][0]["models"]["grok-4.7"]["tool_count"] = 1
        with self.assertRaises(ValueError):
            parse_copilot_response(render(events))

    def test_jsonl_unicode_separators_inside_strings_do_not_split_events(self):
        events = [
            {"type": "user.message", "data": {"content": "code: \x85\u2028\u2029"}},
            {"type": "assistant.message", "data": {
                "model": "grok-4.7", "content": '{"ok":true}', "toolRequests": [],
            }},
            {"type": "session.usage_checkpoint", "data": {
                "promptCacheBreakState": [{"models": {"grok-4.7": {"tool_count": 0}}}],
            }},
            {"type": "result", "exitCode": 0, "sessionId": "test"},
        ]
        stdout = "\n".join(json.dumps(event, ensure_ascii=False) for event in events) + "\n"
        self.assertEqual(parse_copilot_response(stdout)["text"], '{"ok":true}')

    def test_rate_limit_wait_uses_header_and_embedded_message(self):
        response = httpx.Response(
            429, headers={"Retry-After": "30"},
            json={"error": {"message": 'Try again in 43 seconds.'}},
        )
        self.assertEqual(retry_after_seconds(response), 44)
        self.assertEqual(retry_after_seconds(httpx.Response(429)), 61)

    def test_rate_limits_share_cooldown_without_exhausting_annotation_retries(self):
        async def exercise(directory):
            study = Study.__new__(Study)
            study.output = Path(directory)
            study.counts = Counter()
            study.request_gate = RequestGate(20)
            responses = [httpx.Response(429, text="Try again in 43 seconds."),
                         httpx.Response(200, json={"ok": True})]
            transport = httpx.MockTransport(lambda request: responses.pop(0))
            async with httpx.AsyncClient(base_url="https://example.invalid/v1/",
                                         transport=transport) as client:
                with patch.object(study.request_gate, "wait", new_callable=AsyncMock) as wait:
                    with patch.object(study.request_gate, "defer") as defer:
                        response = await study.cloudgpt_response(
                            client, {"model": "test"}, "judge", {"id": "0001"})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(wait.await_count, 2)
            defer.assert_called_once_with(44)
            self.assertEqual(study.counts["provider_rate_limits"], 1)
            self.assertEqual(len((study.output / "rate_limits.jsonl").read_text().splitlines()), 1)
        with tempfile.TemporaryDirectory() as directory:
            asyncio.run(exercise(directory))

    def test_shared_gate_checks_an_extended_cooldown_after_waking(self):
        gate = RequestGate(20)
        clock = [100.0]
        gate.not_before = 105.0
        waits = []

        async def sleep(seconds):
            waits.append(seconds)
            clock[0] += seconds
            if len(waits) == 1:
                gate.defer(7)

        async def exercise():
            with patch("run_multilabel_annotation.time.monotonic", lambda: clock[0]):
                with patch("run_multilabel_annotation.asyncio.sleep", sleep):
                    await gate.wait()
            self.assertEqual(waits, [5.0, 7.0])
            self.assertEqual(gate.not_before, 132.0)
        asyncio.run(exercise())

    def test_resume_rejects_modified_evidence_or_saved_annotation(self):
        import run_multilabel_annotation as runner
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            item = {"id": "0001", "task": "task", "trial": "trial",
                    "configuration": "config", "packet_sha256": digest(self.packet)}
            write_json(output / "manifest.json", [item])
            write_json(output / "protocol.json", {
                "models": MODELS, "transports": TRANSPORTS, "taxonomy": TAXONOMY,
                "rubric_sha256": digest(RUBRIC), "manifest_sha256": digest([item]),
                "runner_sha256": runner.hashlib.sha256(Path(runner.__file__).read_bytes()).hexdigest(),
            })
            write_json(output / "packets/0001.json", self.packet)
            annotation = self.annotation("execution-timeout")
            record = {
                **item, "requested_model": MODELS["A"], "reported_model": "grok-4.7",
                "rubric_sha256": digest(RUBRIC), "other_labels_visible": False,
                "annotation": annotation, "text": json.dumps(annotation),
            }
            write_json(output / "labels/A/0001.json", record)
            study = Study(output, 15, 2)
            self.assertEqual(study.saved("A", item, study.packet(item)), record)
            record["annotation"] = self.annotation("code-adaptation-error")
            write_json(output / "labels/A/0001.json", record)
            with self.assertRaises(ValueError):
                study.saved("A", item, self.packet)
            write_json(output / "packets/0001.json", {**self.packet, "instruction": "changed"})
            with self.assertRaises(ValueError):
                study.packet(item)

    def test_judge_runs_after_both_primaries_and_does_not_union_labels(self):
        import run_multilabel_annotation as runner
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            item = {"id": "0001", "task": "task", "trial": "trial",
                    "configuration": "config", "packet_sha256": digest(self.packet)}
            write_json(output / "manifest.json", [item])
            write_json(output / "protocol.json", {
                "models": MODELS, "transports": TRANSPORTS, "taxonomy": TAXONOMY,
                "rubric_sha256": digest(RUBRIC), "manifest_sha256": digest([item]),
                "runner_sha256": runner.hashlib.sha256(Path(runner.__file__).read_bytes()).hexdigest(),
            })
            write_json(output / "packets/0001.json", self.packet)
            study = Study(output, 15, 2)
            calls = []

            async def annotate(client, coder, selected, prior=None):
                if coder == "judge":
                    self.assertEqual(set(calls), {"A", "B"})
                    self.assertEqual(len(prior), 2)
                calls.append(coder)
                category = "execution-timeout" if coder == "A" else "code-adaptation-error"
                annotation = self.annotation(category)
                record = {
                    **selected, "requested_model": MODELS[coder],
                    "reported_model": MODELS[coder].removeprefix("cloudgpt/"),
                    "rubric_sha256": digest(RUBRIC), "other_labels_visible": coder == "judge",
                    "annotation": annotation, "text": json.dumps(annotation),
                }
                if prior is not None:
                    record["prior_annotations_sha256"] = digest(prior)
                write_json(study.label_path(coder, selected), record)
                return True

            env = {"CLOUDGPT_BASE_URL": "https://example.invalid/v1", "CLOUDGPT_API_KEY": "test"}
            with patch.dict(os.environ, env), patch.object(study, "annotate", annotate):
                asyncio.run(study.run())
            final = json.loads((output / "final.jsonl").read_text())
            self.assertEqual(signature(final["annotation"]),
                             signature(self.annotation("code-adaptation-error")))
            self.assertEqual(final["source"], "astra-adjudication")
            self.assertEqual(read_json(output / "agreement.json")["disagreements"], 1)

            calls.clear()

            async def fail_one_primary(client, coder, selected, prior=None):
                calls.append(coder)
                return coder != "B"

            with patch.dict(os.environ, env), patch.object(study, "annotate", fail_one_primary):
                with self.assertRaises(RuntimeError):
                    asyncio.run(study.run())
            self.assertNotIn("judge", calls)


if __name__ == "__main__":
    unittest.main()
