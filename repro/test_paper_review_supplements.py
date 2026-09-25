#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import unittest

from package_paper_review_supplements import omit_reasoning
from validate_paper_review_supplements import adjudicated_categories, kappa, parse_response, quote_present


class SupplementTests(unittest.TestCase):
    def test_kappa_uses_all_pairs(self):
        agreement, coefficient = kappa([("a", "a"), ("a", "a"), ("b", "b"), ("a", "b")])
        self.assertEqual(agreement, 0.75)
        self.assertEqual(coefficient, 0.5)

    def test_insufficient_evidence_is_a_category(self):
        agreement, coefficient = kappa([("a", "a"), ("a", "b"), ("insufficient-evidence", "b")])
        self.assertEqual(agreement, 1 / 3)
        self.assertEqual(coefficient, 1 / 7)

    def test_degenerate_kappa_is_not_reported_as_success(self):
        for pairs in ([], [("a", "a")]):
            with self.subTest(pairs=pairs), self.assertRaises(SystemExit):
                kappa(pairs)

    def test_citation_normalization(self):
        self.assertTrue(quote_present("a b", "a\\nb"))
        self.assertTrue(quote_present('"version": "1"', '\\"version\\": \\"1\\"'))
        self.assertFalse(quote_present("invented text", "actual evidence"))
        self.assertFalse(quote_present("", "actual evidence"))

    def test_fenced_response(self):
        self.assertEqual(parse_response('```json\n{"category": "a"}\n```'), {"category": "a"})

    def test_reasoning_removal_preserves_labels_and_input(self):
        original = {"category": "a", "responses": [{"reasoning_content": None, "text": "answer"}],
                    "usage": {"reasoning_tokens": 12}}
        cleaned = omit_reasoning(original)
        self.assertEqual(cleaned, {"category": "a", "responses": [{"text": "answer"}],
                                   "usage": {"reasoning_tokens": 12}})
        self.assertIn("reasoning_content", original["responses"][0])

    def test_adjudication_preserves_consensus_and_original_abstention(self):
        paired = [
            {"id": "001", "disposition": "incomplete-migration"},
            {"id": "002", "disposition": "annotator-disagreement"},
            {"id": "003", "disposition": "insufficient-evidence"},
        ]
        self.assertEqual(adjudicated_categories(paired, {
            "002": {"category": "compile-namespace-inconsistency"},
        }), {"001": "incomplete-migration", "002": "compile-namespace-inconsistency",
             "003": "insufficient-evidence"})

    def test_adjudication_rejects_missing_and_extra_cases(self):
        paired = [{"id": "001", "disposition": "annotator-disagreement"}]
        for decisions in ({}, {"001": {"category": "a"}, "002": {"category": "b"}}):
            with self.subTest(decisions=decisions), self.assertRaises(SystemExit):
                adjudicated_categories(paired, decisions)


if __name__ == "__main__":
    unittest.main()
