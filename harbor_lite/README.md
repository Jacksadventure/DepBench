# harbor_lite

`harbor_lite` runs local coding-agent CLIs against local workspaces and collects
their logs, artifacts, and trajectories into a Harbor-like job directory.

It is intentionally smaller than Harbor: no Docker, no verifier, no benchmark
registry. It is useful when you trust the local checkout, want to use existing
CLI subscriptions, and still want a durable job layout that can be inspected
later.

## Install

This repository intentionally uses a flat layout:

```text
harbor_lite/
  __init__.py
  agents/
    __init__.py
    base.py
    codex.py
    gemini.py
    qwen.py
    claude.py
    opencode.py
  runtime.py
  workspace.py
  trajectory.py
  artifacts.py
  runs.py
```

From another project, import it directly by putting this directory on
`PYTHONPATH`:

```bash
export PYTHONPATH=/path/to/parent:$PYTHONPATH
```

or install it editable:

```bash
pip install -e /path/to/harbor_lite
```

or with `uv`:

```bash
uv add --editable /path/to/harbor_lite
```

The import package is `harbor_lite`.

## Minimal Example

```python
from pathlib import Path

from harbor_lite import CodexAgent, RunSpec, WorkspaceSpec, run_one

spec = RunSpec(
    name="demo",
    agent=CodexAgent(model="gpt-5.4"),
    prompt="Inspect the repo and write NOTES.md with your findings.",
    workspace=WorkspaceSpec.from_local_repo(
        repo_path=Path("/repos/example"),
        base_commit="abc123",
    ),
    copied_paths=("pyproject.toml", "src/**"),
    artifact_paths=("NOTES.md", ".agents/**"),
)

result = run_one(spec, jobs_dir=Path("jobs"), workspace_root=Path("workspace"))
print(result.job_dir)
```

## Main Ideas

- One subclass per agent: `CodexAgent`, `GeminiAgent`, `QwenAgent`,
  `ClaudeAgent`, `OpenCodeAgent`.
- Agent subclasses act as adapters: each one declares the Harbor-facing agent
  name, CLI runner, default model, command line, log filename, and native
  session files to collect and convert into ATIF trajectory steps.
- `model=` is explicit on every agent object.
- `disable_web=True` adds known CLI flags where supported. Pass
  `extra_args=(...)` for local CLI versions that need custom flags.
- `isolated_state=True` gives each run a fresh `HOME` and agent state dirs so
  agents do not read global memories. Credentials should come from environment
  variables or project-local CLI configuration.
- `WorkspaceSpec.from_local_repo(...)` clones a local repository, checks out the
  snapshot commit, runs `git clean -fdx`, and prunes refs/reflogs so normal
  `git log` only exposes history reachable from the snapshot.
- `copied_paths` and `artifact_paths` are globs relative to the workspace.
- The agent's live output is written under the trial artifact directory, e.g.
  `artifacts/codex.txt`, while a copy is also placed under `agent/`.
- Non-zero agent exits write `exception.txt` with the tail of the live log.

## Batch Runs

```python
from harbor_lite import run_many

results = run_many(specs, concurrency=3, jobs_dir="jobs", workspace_root="workspace")
```

Each trial receives `status.json`; the job root receives `summary.json`.
`run_one()` and `run_many()` also print concise progress lines by default:

```text
[21:15:00] case-ok preparing: workspace=workspace/job/case-ok/repo prompt='...'
[21:15:00] case-ok running: agent=codex model=gpt-5.4 log=jobs/job/case-ok/artifacts/codex.txt
[21:16:42] [17/438] case-ok completed: duration=1m42s artifacts=jobs/job/case-ok/artifacts
```

Pass `quiet=True` to disable console progress.

## Output Layout

```text
jobs/<job-name>/
  config.json
  result.json
  summary.json
  <trial-name>/
    status.json
    exception.txt          # only on non-zero exit
    agent/
      trajectory.json      # when conversion is available
      codex.txt
      sessions/
    artifacts/
      manifest.json
      codex.txt            # live log, updated while the agent runs
      ... copied artifacts from artifact_paths ...
```

The package can write this layout without Harbor installed. `TrajectoryCollector`
writes an ATIF-v1.7 `trajectory.json` from structured agent logs/session files
where possible, and still preserves raw logs/session files for debugging when a
CLI changes format.

If Harbor is installed, inspect the run with:

```bash
harbor view jobs/
```
