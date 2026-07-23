#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TASKS_ROOT = ROOT / "dataset/tasks"
TASK_SUMMARY = ROOT / "dataset/task_summary.json"


AGENTS = {
    "codex": "custom_agents.codex:CustomCodex",
    "copilot_cli": "custom_agents.copilot_cli:CustomCopilotCli",
    "opencode": "custom_agents.opencode:CustomOpenCode",
    "claude_code": "custom_agents.claude_code:CustomClaudeCode",
}


DEFAULT_KWARGS = {
    "codex": {
        "version": "0.130.0",
        "provider_name": "depbench-openai",
        "wire_api": "responses",
        "requires_openai_auth": False,
        "disable_web_tools": True,
    },
    "copilot_cli": {
        "version": "1.0.64",
        "disable_web_tools": True,
    },
    "opencode": {
        "version": "1.17.11",
        "default_provider": "openai",
        "disable_web_tools": True,
    },
    "claude_code": {
        "disable_nonessential_traffic": True,
    },
}


def task_names(args: argparse.Namespace) -> list[str] | None:
    if args.all_tasks:
        return sorted(row["folder"] for row in json.loads(TASK_SUMMARY.read_text()))
    if args.task:
        for task in args.task:
            if not (TASKS_ROOT / task).is_dir():
                raise SystemExit(f"unknown task: {task}")
        return args.task
    return None

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent", choices=sorted(AGENTS), required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--task", action="append", help="task folder name; repeat for multiple tasks")
    parser.add_argument("--all-tasks", action="store_true")
    parser.add_argument("--concurrency", type=int, default=1)
    parser.add_argument("--jobs-dir", default="harbor_jobs")
    parser.add_argument("--memory-mb", type=int, default=8192)
    parser.add_argument("--max-retries", type=int, default=0)
    parser.add_argument("--absolute-paths", action="store_true", help="write absolute dataset paths instead of release-root-relative paths")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    if args.all_tasks and args.task:
        raise SystemExit("--all-tasks and --task are mutually exclusive")

    if not TASKS_ROOT.is_dir() or not TASK_SUMMARY.is_file():
        raise SystemExit(
            "benchmark dataset not found; run: python3 repro/download_benchmark.py"
        )

    dataset_path = str(TASKS_ROOT if args.absolute_paths else Path("dataset/tasks"))
    config = {
        "jobs_dir": args.jobs_dir,
        "n_attempts": 1,
        "timeout_multiplier": 1.0,
        "debug": False,
        "n_concurrent_trials": args.concurrency,
        "quiet": False,
        "retry": {
            "max_retries": args.max_retries,
            "exclude_exceptions": [
                "VerifierTimeoutError",
                "AgentTimeoutError",
                "RewardFileEmptyError",
                "RewardFileNotFoundError",
                "VerifierOutputParseError",
            ],
        },
        "environment": {
            "type": "docker",
            "force_build": False,
            "delete": True,
            "override_memory_mb": args.memory_mb,
            "env": {},
            "kwargs": {},
        },
        "verifier": {
            "env": {},
            "disable": False,
        },
        "artifacts": [],
        "metrics": [],
        "datasets": [
            {
                "path": dataset_path,
                "task_names": task_names(args),
            }
        ],
        "agents": [
            {
                "import_path": AGENTS[args.agent],
                "model_name": args.model,
                "kwargs": DEFAULT_KWARGS[args.agent],
                "env": {},
            }
        ],
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(config, indent=2, sort_keys=True) + "\n")
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
