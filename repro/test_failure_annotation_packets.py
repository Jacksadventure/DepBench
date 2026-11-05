#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import csv
import gzip
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import build_failure_annotation_packets as packets
from run_multilabel_annotation import prepare, read_json


class PacketSelectionTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.artifact = self.root / "paper_review"
        self.configurations = ["gemini35flash__opencode"] + [
            f"other-model-{index}__harness" for index in range(9)
        ]
        self.task = "example__repo__1"
        task_dir = self.artifact / "dataset/tasks" / self.task
        (task_dir / "solution").mkdir(parents=True)
        (task_dir / "instruction.md").write_text("Upgrade the dependency.")
        for name in ("code.patch", "manifest.patch"):
            (task_dir / "solution" / name).write_text("-old\n+new\n")
        outcomes = []
        for index, configuration in enumerate(self.configurations):
            reward = None if index == 9 else 0.0
            row = {
                "task": self.task, "trial": f"trial-{index}", "reward": reward,
                "trajectory": {"steps": [{"source": "agent", "message": "Attempted repair"}]},
                "verifier_test_stdout": "Test failed",
            }
            for directory in ("trajectories", "verify_logs"):
                path = self.artifact / directory / f"{configuration}.jsonl.gz"
                path.parent.mkdir(parents=True, exist_ok=True)
                with gzip.open(path, "wt", encoding="utf-8") as handle:
                    handle.write(json.dumps(row) + "\n")
            outcomes.append({
                "configuration": configuration, "task": self.task,
                "final_trial": row["trial"], "final_reward": "" if reward is None else str(reward),
                "outcome_source": "original",
            })
        outcomes.append({
            "configuration": self.configurations[0], "task": "passed",
            "final_trial": "pass-trial", "final_reward": "1",
            "outcome_source": "original",
        })
        path = self.artifact / "results/final_per_task_outcomes.csv"
        path.parent.mkdir()
        with path.open("w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=outcomes[0].keys())
            writer.writeheader()
            writer.writerows(outcomes)

    def test_default_cli_exports_all_configurations_without_main_dataset(self):
        output = self.root / "packets.json"
        with patch.object(packets, "ROOT", self.root):
            with patch("sys.argv", ["packets", "--output", str(output)]):
                self.assertEqual(packets.main(), 0)
        rows = read_json(output)
        self.assertEqual({row["configuration"] for row in rows}, set(self.configurations))
        self.assertEqual(len(rows), 10)
        self.assertEqual(sum(row["reward"] is None for row in rows), 1)
        self.assertTrue(all(row["instruction"] == "Upgrade the dependency." for row in rows))

    def test_multilabel_preparation_uses_same_all_configuration_nonpass_cohort(self):
        output = self.root / "study"
        prepare(self.artifact, output, None)
        manifest = read_json(output / "manifest.json")
        expected = packets.select_requests(self.artifact)
        identity = lambda row: (row["configuration"], row["task"], row["trial"], row["reward"])
        self.assertEqual({identity(row) for row in manifest}, {identity(row) for row in expected})

    def test_explicit_filters_and_manifest_do_not_silently_change_scope(self):
        selected = packets.select_requests(self.artifact, configurations=self.configurations[1:3])
        self.assertEqual({row["configuration"] for row in selected}, set(self.configurations[1:3]))
        with self.assertRaises(ValueError):
            packets.select_requests(self.artifact, configurations=["missing"])
        manifest = self.root / "manifest.json"
        manifest.write_text(json.dumps(selected))
        (self.artifact / "results/final_per_task_outcomes.csv").unlink()
        self.assertEqual(packets.select_requests(self.artifact, manifest), selected)
        manifest.write_text(json.dumps(selected + selected))
        with self.assertRaises(ValueError):
            packets.select_requests(self.artifact, manifest)

    def test_packet_rejects_mismatched_trials_or_rewards(self):
        requested = packets.select_requests(self.artifact)[0]
        path = self.artifact / "trajectories" / f"{requested['configuration']}.jsonl.gz"
        trajectory = packets.read_jsonl(path)[self.task]
        for verifier in (
            {**trajectory, "trial": "wrong-trial"},
            {**trajectory, "reward": 1.0},
        ):
            with self.subTest(verifier=verifier), self.assertRaises(ValueError):
                packets.build_packet(requested, trajectory, verifier, 1000,
                                     artifact_root=self.artifact)


if __name__ == "__main__":
    unittest.main()
