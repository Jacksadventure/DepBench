# Harbor Harness — depbot dependency-upgrade benchmark

> Snapshot taken: **2026-06-23 00:45 UTC**
> Current dataset source of truth: **`harbor_benchmark/tasks_v4/` = 219 tasks**
> Current ecosystem mix: **npm/yarn 79 · Maven/Java 66 · Go 41 · Cargo/Rust 21 · Python 12**
> Task metadata schemas: **110 `schema_version = "1.1"` tasks · 109 legacy `version = "1.0"` tasks**
> Index file: **`harbor_benchmark/task_summary.json` = 219 rows**, regenerated from `tasks_v4` on 2026-06-23
> Stale parquet note: **`pass_dataset_v4.parquet` still has 218 rows** and is not the authoritative v4 source until rebuilt.

This document captures the **current Harbor harness and dataset state** so we can A/B different settings later. Variant log is at the bottom — append a new revision when settings change.

---

## 1. End-to-end pipeline

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  Runtime phase (prebuilt image)                                             │
│  ──────────────────────────────                                             │
│  1. task.toml points Harbor at docker_image                                 │
│  2. force_build=false makes Harbor use docker-compose-prebuilt.yaml         │
│  3. environment/docker-compose.yaml is only a placeholder for validation    │
│  4. dependency-upgrade manifest patch stays outside the agent image         │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  Agent phase (timeout 1800s)                                                │
│  ────────────────────────                                                   │
│  Container starts. Agent is given:                                          │
│    • /app  ← repo at base_sha                                               │
│    • instruction text as the agent prompt                                   │
│  Agent does NOT see:                                                        │
│    • manifest.patch (dependency patch; oracle-only)                         │
│    • code.patch (oracle solution)                                           │
│    • test.patch (canonical post-upgrade tests)                              │
│  Agent performs the dependency upgrade, edits /app source files, and exits. │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  Verify phase (timeout 300s)                                                │
│  ─────────────────────────                                                  │
│  Verifier mounts /tests/ (incl. hidden test.patch) and runs tests/test.sh:  │
│    1. install uv + pytest 8.4.1 + pytest-json-ctrf                          │
│    2. pytest /tests/test_state.py                                           │
│       • test_dependency_upgrade_fix:                                        │
│           – git apply test.patch onto /app  (canonical post-upgrade tests)  │
│           – subprocess.run(<test_cmd>, cwd=/app)                            │
│           – assert returncode == 0                                          │
│    3. write 1 or 0 to /logs/verifier/reward.txt                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

Key invariant: the agent is graded against a **fixed test.patch**. Even if it modified the working tree, the verifier overlays test.patch right before running tests, so the oracle test set is identical across every trial. Under the current prebuilt-image setup, the dependency manifest patch is not baked into `/app` and is not visible to the agent; the agent must infer and perform the upgrade from the instruction.

---

## 2. Per-task scaffold layout

```
harbor_benchmark/tasks_v4/<folder>/
├── instruction.md                      # what the agent sees
├── task.toml                           # metadata + timeouts + resources
├── environment/
│   ├── docker-compose.yaml             # placeholder; runtime uses docker_image
│   └── patches/
│       └── manifest.patch              # dep upgrade source copy (not agent-visible)
├── solution/                           # oracle, hidden from agent
│   ├── manifest.patch                  # dep upgrade patch copied for oracle use
│   ├── solve.sh                        # applies manifest.patch, then code.patch
│   └── code.patch                      # gold source-code fix (may be empty)
└── tests/                              # uploaded only at verify phase
    ├── test.sh                         # entry point that pytest runs
    ├── test_state.py                   # applies test.patch then runs test_cmd
    └── test.patch                      # canonical post-upgrade tests (hidden)
```

Current `tasks_v4` contains **219 tasks**:

| Ecosystem | Tasks |
|---|---:|
| npm/yarn | 79 |
| Maven/Java | 66 |
| Go | 41 |
| Cargo/Rust | 21 |
| Python | 12 |

The Cargo/Rust subset was pruned with the rest of the dataset after the non-witness audit. The clean205 snapshot keeps 20 Cargo/Rust tasks; the current curated v4-with-test branch keeps 21 after adding one hard Cargo import.

---

## 3. Canonical task example: `peopledatalabs__peopledatalabs-python__55`

PR: https://github.com/peopledatalabs/peopledatalabs-python/pull/55
Upgrade: `black 22.12.0 → 23.3.0` (pip ecosystem)

### 3.1 `task.toml`

```toml
version = "1.0"

[metadata]
author_name = "depbot-benchmark"
author_email = "depbot@benchmark.dev"
difficulty_explanation = "Requires understanding breaking changes in black 22.12.0 -> 23.3.0 and adapting source code accordingly"
solution_explanation = "Apply the code changes from the original PR that fixed the dependency upgrade"
verification_explanation = "Run the project test suite and verify all tests pass"
category = "dependency-upgrade"
tags = ["pip", "breaking-change", "dependency-upgrade"]
expert_time_estimate_hours = 0.5

[verifier]
timeout_sec = 300.0

[agent]
timeout_sec = 1800.0

[environment]
build_timeout_sec = 900.0
cpus = 2
memory_mb = 4096
storage_mb = 20480
gpus = 0
```

### 3.2 `environment/docker-compose.yaml`

```yaml
# Prebuilt-image placeholder. Harbor uses task.toml [environment].docker_image
# when force_build=false; do not add build instructions here.
services: {}
```

> The historical Dockerfiles were removed after publishing the strict prebuilt images to avoid confusion. Each task now keeps a minimal compose placeholder because Harbor's Docker environment validation requires either a Dockerfile or a task compose file. The actual runtime image comes from `[environment].docker_image` in `task.toml` when job configs set `force_build=false`. The dependency-upgrade manifest patch is not copied into the agent-visible image; a duplicate lives at `solution/manifest.patch` so `solution/solve.sh` can apply it for oracle/sanity runs before replaying the relevant post-manifest setup.

### 3.3 `instruction.md` (agent-visible)

```markdown
# Dependency Upgrade Fix: black 22.12.0 → 23.3.0

## Context

You are working on the **peopledatalabs/peopledatalabs-python** Python (pip/poetry) project.
The dependency **`black`** has been upgraded from version **22.12.0** to **23.3.0** in the
project's manifest/lock files. This upgrade introduces breaking changes that cause test
failures.

You must perform the dependency upgrade yourself, end-to-end. Update the project's
manifest and lock files to apply the dependency bump, then adapt the source code so that
the upgraded project's test suite passes against the new version of the dependency.

## Working Directory

The project source code is located at `/app`.

## Upstream Release Notes

The following is the original pull-request description for this dependency bump,
including the upstream release notes / changelog. ...

**PR title:** <fetched from GitHub>

**PR body:**
<cleaned dependabot body, dropped HTML/<details>, max 4000 chars>

## Constraints

- **Do not modify any test files.** The test suite is the evaluation oracle and will be
  re-applied verbatim before grading.
- Restrict your changes to the project's source code so that the existing tests pass
  against the upgraded dependency.
```

### 3.4 `solution/solve.sh` (oracle, hidden from agent)

```bash
#!/bin/bash
set -euo pipefail
cd /app

git apply /tmp/manifest.patch || git apply --3way /tmp/manifest.patch
pip install pytest && pip install -e .

if [ -s /solution/code.patch ]; then
    git apply /solution/code.patch || git apply --3way /solution/code.patch
else
    echo 'code.patch empty: nothing to apply.'
fi
```

### 3.5 `tests/test.sh` (verifier entrypoint)

```bash
#!/bin/bash
apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

curl -LsSf https://astral.sh/uv/0.9.7/install.sh | sh
source $HOME/.local/bin/env

uvx \
  --with pytest==8.4.1 \
  --with pytest-json-ctrf==0.3.5 \
  pytest --ctrf /logs/verifier/ctrf.json /tests/test_state.py -rA

if [ $? -eq 0 ]; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi
```

### 3.6 `tests/test_state.py` (the actual grading test)

```python
import subprocess, os

TEST_PATCH = "/tests/test.patch"

def _apply_test_patch():
    """Apply the hidden test patch into /app right before grading."""
    if not os.path.exists(TEST_PATCH) or os.path.getsize(TEST_PATCH) == 0:
        return
    for cmd in (
        ["git", "apply", "--whitespace=nowarn", TEST_PATCH],
        ["git", "apply", "--whitespace=nowarn", "--3way", TEST_PATCH],
        ["git", "apply", "--whitespace=nowarn", "--reject", TEST_PATCH],
    ):
        r = subprocess.run(cmd, cwd="/app", capture_output=True, text=True)
        if r.returncode == 0:
            return
    raise RuntimeError(f"Failed to apply hidden test patch:\n{r.stdout}\n{r.stderr}")


def test_dependency_upgrade_fix():
    _apply_test_patch()
    result = subprocess.run(
        "pytest -k 'not test_api_endpoint_' tests/",   # ← per-task `test_cmd`
        shell=True, cwd="/app",
        capture_output=True, text=True, timeout=240,
    )
    assert result.returncode == 0, (
        f"Test command failed with exit code {result.returncode}\n"
        f"STDOUT:\n{result.stdout[-2000:]}\n"
        f"STDERR:\n{result.stderr[-2000:]}"
    )
```

---

## 4. Patch contracts (what is in each `.patch`)

| Patch | Origin | Visibility to agent | When applied | Purpose |
|---|---|---|---|---|
| `environment/patches/manifest.patch` | original PR `manifest_patch` field | **YES** | Agent-time for task solving; oracle-time in `solution/solve.sh` | Bumps `package.json`/`requirements.txt`/`go.mod`/`Cargo.toml` + lockfiles |
| `tests/test.patch` | original PR `test_patch` field (cleaned for rescued) | **NO** | Verify-time, by `test_state.py` | Canonical post-upgrade test suite |
| `solution/code.patch` | original PR `code_patch` field (cleaned for rescued) | **NO** | Only when running `solve.sh` after `manifest.patch` (oracle/sanity) | Gold source fix |

For the 175 rescued tasks, `code.patch` and `test.patch` have been stripped of drive-by changes by the rescue sub-agents (see `_rescue_v2/RESCUE_REPORT.md`). For 14 tasks (mostly the PDL family) `code.patch` ended up empty — `solve.sh` has a `[ -s ]` guard that no-ops.

---

## 5. Harbor job configuration

`_run_configs/copilot_cli_rescue258_2026-04-28__03-38-08.json`:

```json
{
  "job_name": "copilot_cli_rescue258_2026-04-28__03-38-08",
  "jobs_dir": "harbor_jobs",
  "n_attempts": 1,
  "n_concurrent_trials": 6,
  "timeout_multiplier": 1.0,
  "quiet": true,
  "retry": {
    "max_retries": 0,
    "exclude_exceptions": [
      "VerifierTimeoutError", "AgentTimeoutError",
      "RewardFileEmptyError", "RewardFileNotFoundError",
      "VerifierOutputParseError"
    ]
  },
  "environment": {
    "type": "docker",
    "force_build": false,
    "delete": true
  },
  "agents": [
    {"name": "copilot-cli"}              // default model = whatever copilot-cli ships
  ],
  "datasets": [
    {"path": "/Data2/v-zijianluo/depbot/harbor_benchmark/tasks_v4"}   // current pruned v4 tasks
  ]
}
```

### Launch command (idiom)

```bash
nohup bash -c "
  export DOCKER_HOST=unix:///run/user/1900/docker.sock
  export GH_TOKEN=\$(cat ~/.local/share/copilot-api/github_token)
  export GITHUB_TOKEN=\$GH_TOKEN
  export COPILOT_GITHUB_TOKEN=\$GH_TOKEN
  harbor run --config _run_configs/<config>.json
" > harbor_jobs/<job>.stdout.log 2>&1 &
```

A simple watchdog (`watchdog.sh`) cycles every 30s and `docker rm -f`s any container with name pattern `__*` that has been "Up X minutes" with X > 10, to clean up stuck containers from the 1800s agent timeouts.

### Agent install (per trial setup)

```bash
# auto-detected by harbor based on agent name; runs inside the agent container
apt-get install -y curl bash git
curl -fsSL https://gh.io/copilot-install | bash
export PATH="$HOME/.local/bin:$PATH"
copilot --version
```

Then for each trial:

```bash
copilot --prompt='<contents of instruction.md>' --add-dir /app --allow-tool '*'
```

(Exact flags are baked into harbor's `copilot-cli` adapter.)

---

## 6. Code generators (single source of truth)

The current `tasks_v4` directory is assembled from multiple generator passes:

- `convert_to_harbor.py` generated the original dependency-upgrade task scaffold.
- `v3_transform.py` converted tasks to the no-manifest-preapply harness shape.
- `_maven_bot_oracle/convert_maven_a_to_harbor.py` added revised Maven Tier-A tasks.
- Cargo Tier-A tasks were added from `_github_cargo_crawl/oracle/dataset/cargo_level1_oracle_tier_a.jsonl`; cases repaired from infra/toolchain drift keep their verified Rust image and command overrides.

The original scaffold helpers in `convert_to_harbor.py` are:

| Function | What it produces |
|---|---|
| `generate_instruction(row, info)` | `instruction.md` (incl. cleaned PR body from `_pr_bodies/<folder>.json`) |
| `generate_dockerfile(row)` | `environment/Dockerfile` (later transformed so `manifest.patch` is copied but not pre-applied) |
| `generate_task_toml(row, info)` | `task.toml` (timeouts: agent 1800s, verifier 300s, build 900s; 2 cpu / 4 GB RAM / 20 GB disk) |
| `generate_solve_sh(row)` | `solution/solve.sh` (with empty-patch guard) |
| `generate_test_sh(row)` | `tests/test.sh` (uv + pytest 8.4.1) |
| `generate_test_state_py(row)` | `tests/test_state.py` (apply test.patch + run per-task `test_cmd`) |
| `convert_row(row, info)` | bundles all the above + writes manifest/code/test patches into the task dir |
| `parse_upgrade_info(manifest_patch, ecosystem)` | extracts `library`, `old_version`, `new_version` from the manifest diff |

The `instruction.md` PR-body injection comes from `_load_pr_metadata(folder)` reading `_pr_bodies/<folder>.json`, then `_clean_pr_body` strips:

- `<details><summary>Dependabot commands…</summary>` block (and beyond)
- `<!-- dependabot ... -->` markers
- `<details><summary>X</summary>` → `### X`
- `<a href="…">X</a>` → `[X](…)`, `<code>` → backticks, all other tags
- HTML entity unescape, blank-line collapse, truncated to 4000 chars

---

## 7. Snapshot of run @ 2026-04-28 11:42 UTC

| | |
|---|---|
| Job ID | `copilot_cli_rescue258_2026-04-28__03-38-08` |
| Started | 2026-04-28 03:38 UTC |
| Elapsed | 8h 04m |
| Trials done | 186/258 (72%) |
| In-flight | ~10 |
| Concurrency | 6 |
| Watchdog | running, no stuck containers reaped recently |

### Latest reward stats

```
                 PASS  FAIL    n  PASS%
rescued (175):    30    69    99   30.3%   (76 still pending or in-flight at last check)
original (83):    15    40    55   27.3%   (28 still pending or in-flight at last check)
TOTAL :           45    109  154   29.2%
```

(Numbers refresh on each `tail` run; final summary will be in `harbor_jobs/<job>/result.json`.)

---

## 8. Variant log (append on each new setting)

### v4 clean witnessed frozen-run policy — 205 tasks (2026-06-22)

- **Benchmark baseline remains**: the 2026-06-19 clean witnessed `tasks_v4` snapshot with **205** tasks.
- **Launch policy**: multi-hour Harbor runs must target a **frozen dataset snapshot path** (for example, a detached worktree or immutable copied tree), not the mutable working-tree path `harbor_benchmark/tasks_v4/`.
- **Reason**: a 2026-06-22 OpenCode Gemini rerun launched against the old 228-task mutable path became invalid after the branch moved `tasks_v4` to the pruned 205-task snapshot mid-run, which later caused `FileNotFoundError` on removed task directories.
- **Comparison policy**: the 228-task Gemini Copilot/OpenCode artifacts are historical postmortem evidence only. Fresh benchmark comparisons should use the frozen clean205 baseline.

### v4 clean witnessed snapshot — 205 tasks in `tasks_v4` (2026-06-19)

- **Current authoritative dataset path**: `harbor_benchmark/tasks_v4/`.
- **Task count**: **205** task directories, all with `task.toml`.
- **Ecosystem mix**: npm/yarn 79 · Maven/Java 66 · Go 28 · Cargo/Rust 20 · Python 12.
- **Metadata schemas**: 96 tasks use `schema_version = "1.1"` and 109 tasks use legacy `version = "1.0"`.
- **Index**: `harbor_benchmark/task_summary.json` regenerated from `tasks_v4` with 205 rows.
- **Drop-list removal**: removed the remaining 23 non-clean current tasks from the 228-task snapshot. The retained set now matches the 2026-06-18 static-audit `WITNESSES_BREAKING_CHANGE` intersection with the current task tree.
- **Current static validation**: 205 task dirs · `task_summary.json=205` · drop-list directories absent from `tasks_v4`.


### v4 with-test addition — 14 hard tasks retained (2026-06-23)

- Initially imported **52** oracle-passing dependency-upgrade tasks from the with-test small pool, then retained only **14** harder/cleaner tasks after the GPT-5.5 quality audit.
- The import split upstream repair patches into v4 layout: production hunks in `solution/code.patch`, repository test hunks in hidden `tests/test.patch`, and manifest hunks in both `environment/patches/manifest.patch` and `solution/manifest.patch`.
- Rebuilt and pushed v4 prebuilt images as `idk233333/depbench-task-images:v4test-<task>`, with static verification that no manifest patch leaked into the image.
- Oracle validation job: `harbor_jobs/oracle_v4_with_tests_small_59_20260622__1505-00` — **52 pass / 7 fail / 0 exceptions**. The failed 7 and one unavailable PR (`FollowTheProcess__metrics__50`) were not imported.
- Post-audit current `tasks_v4` count: **219**. Ecosystem mix: npm/yarn 79 · Maven/Java 66 · Go 41 · Cargo/Rust 21 · Python 12.

- Quality audit policy for imported tasks: keep only tasks with clean hidden-test paths, non-weak test deltas, and not solved by all three main GPT-5.5 agents (Copilot CLI, Codex, and OpenCode). Removed **38** imported tasks as weak/easy; retained **14** hard imports.
- Merged GPT-5.5 results for the current 219-task dataset: Codex **0.479** (105/219), Copilot CLI **0.449** (97/216 reward-bearing; 3 no-reward), OpenCode **0.429** (94/219). Report: `harbor_benchmark/reports/v4_with_test219_summary_2026-06-23.json`.
- Supplemental hard14-only result: Claude Code/GPT-5.5 **0.143** (2/14, all with `NonZeroAgentExitCodeError`).
- Full Gemini 3.5 Flash results for the current 219-task dataset: Copilot CLI **0.225** (49/218 reward-bearing; 1 no-reward), OpenCode **0.174** (38/219). Report: `harbor_benchmark/reports/v4_with_test219_summary_2026-06-23.json`.
- Import report: `harbor_benchmark/reports/with_tests_v4_import_20260622.json`.

### v4 dataset snapshot — 228 tasks in `tasks_v4` (2026-06-18)

- **Current authoritative dataset path**: `harbor_benchmark/tasks_v4/`.
- **Task count**: **228** task directories, all with `task.toml`.
- **Ecosystem mix**: npm/yarn 95 · Maven/Java 67 · Go 31 · Cargo/Rust 22 · Python 13.
- **Metadata schemas**: 106 tasks use `schema_version = "1.1"` and 122 tasks use legacy `version = "1.0"`.
- **Index**: `harbor_benchmark/task_summary.json` regenerated from `tasks_v4` with 228 rows.
- **Non-witness pruning**: 69 tasks were removed from the 297-task snapshot after blind file-level review of the 92 non-clean audit cases. The retained set is 205 clean `WITNESSES_BREAKING_CHANGE` cases plus 14 `KEEP` and 9 `DYNAMIC` cases from `clean_set_pruning_recommendations_2026-06-18`.
- **No-preapply audit**: a 2026-06-15 rerun dry start exposed 27 residual Dockerfiles that still applied `manifest.patch` from alternate paths (`/app/manifest.patch`, `/benchmark/manifest.patch`, `.harbor_manifest.patch`, or `/app/.harbor/manifest.patch`) during image build. These were first converted to copy-only behavior, then the image-visible copy was removed entirely. The final v4 task layout removes Dockerfiles altogether, relies on prebuilt `docker_image` entries, and has oracle `solve.sh` apply `solution/manifest.patch` before replaying the original post-manifest setup commands and `code.patch`.
- **Current static validation**: 228 task dirs · `docker_image=228` · `environment_dockerfiles=0` · `compose_placeholders=228` · `solution_manifest_copies=228` · `empty_test_patch=0` · `non_exec_scripts=0` · `solve_syntax_errors=0`.
- **Cargo update**: the current Cargo oracle Tier-A set has 17 cases. `tasks_v4` already had `oxidecomputer__dropshot__580` and `regexident__cargo-modules__122`; fifteen additional Cargo Tier-A directories were added on 2026-06-15. The newly repaired Cargo A cases preserve their verified harness settings:
  - `Stranger6667__jsonschema__825`: `rust:1.86-bullseye`, subdir `crates/jsonschema`, `git submodule update --init --recursive && cargo fetch`, `cargo test --no-fail-fast --all-features`
  - `omjadas__hudsucker__88`: `rust:1.88-bullseye`, `cargo test --lib --no-run --no-default-features --features rcgen-ca,rustls-client`
  - `rash-sh__rash__698`: `rust:1.85-bullseye`, `cargo test --locked`
  - `regexident__cargo-modules__389`: `rust:1.91-bullseye`, `cargo test --release`
- **Parquet caveat**: `pass_dataset_v4.parquet` and `pass_dataset_clean.parquet` still contain the older 218-row non-Maven snapshot. Use `tasks_v4` and `task_summary.json` as the v4 source until parquet is explicitly rebuilt.

### copilot-cli + codex-cli with `gpt-5.5` on v3-155 (2026-05-15 → 2026-05-17)

Dual-agent run with the **same model (`gpt-5.5`)** on the same 155-task minimal-instruction v3 baseline, to isolate agent-harness effects from model effects.

**Result (final, both runs complete):**

| Agent | Model | Run dir | PASS | FAIL | ERR | pass% | mean |
|---|---|---|---:|---:|---:|---:|---:|
| copilot-cli (1.0.42) | gpt-5.5 | `harbor_jobs/copilot_cli_gpt55_v3_full155_2026-05-15__07-50-00/` | **57** | 93 | 5 | **36.8 %** | 0.375 |
| codex-cli (0.130.0, Maestro) | gpt-5.5 | `harbor_jobs/codex_gpt55_v3_full155_2026-05-16__13-50-00/` | 42 | 110 | 3 | **27.1 %** | 0.275 |

By ecosystem (PASS / total):

| ecosystem | copilot+gpt5.5 | codex+gpt5.5 (fixed) |
|---|---|---|
| pip          | 9 / 18 = **50.0 %** | 8 / 18 = 44.4 % |
| go_modules   | 14 / 35 = **40.0 %** | 8 / 35 = 22.9 % |
| npm_and_yarn | 31 / 92 = 33.7 % | 23 / 92 = 25.0 % |
| cargo        | 3 / 10 = 30.0 % | 3 / 10 = 30.0 % |

Cross-task matrix on the same 155 tasks:

| copilot \ codex | codex PASS | codex FAIL | codex ERR |
|---|---:|---:|---:|
| copilot PASS | 38 | 19 | 0 |
| copilot FAIL | 4 | 89 | 0 |
| copilot ERR  | 0 | 2 | 3 |

→ 89 tasks both fail (likely v2-style hold-out hidden-test mismatch); 19 tasks copilot solves but codex doesn't; only 4 tasks codex solves but copilot doesn't. Agent-asymmetric capability is substantial.

**Codex transport-failure rerun history (important):**

- First codex run on 2026-05-15 (`harbor_jobs/codex_gpt55_v3_full155_2026-05-15__07-50-00/`) reported 28 PASS / 124 FAIL / 3 ERR = 18.1 %. Subagent deep-dive (`_codex_v3_full155_deepdive_2026-05-16.md`) found this run was **NOT actually testing gpt-5.5 nor the agent**: median agent runtime was **6.7s**, with **zero tool calls and zero file edits across all 155 trials**, and 152/155 logs showed ChatGPT auth/websocket 401 failures (`refresh_token_reused`, `token_expired`, `wss://chatgpt.com/backend-api/codex/responses`). The 28 "PASS" labels were verifier-baseline passes (oracle accepted the unmodified repo) and should not be attributed to codex behavior.
- **Root cause**: the run config had `agent.env: {}` so `CODEX_MAESTRO_BASE_URL` / `CODEX_FORCE_API_KEY` / `OPENAI_API_KEY` were never set, the `CodexMaestro` shim therefore wrote no Maestro provider block to `$CODEX_HOME/config.toml`, and `codex exec` fell through to its default ChatGPT OAuth path (which is unreachable from inside the harness container). Additionally, the shim's docstring claimed to override `run()` to inject `-c model_provider=agent-maestro`, but no such override existed.
- **Fix applied** to `_run_configs/codex_gpt55_v3_full155_2026-05-16__13-50-00.json`:
  ```json
  "env": {
    "CODEX_MAESTRO_BASE_URL": "http://172.100.216.1:23333/api/openai/v1",
    "CODEX_FORCE_API_KEY": "1",
    "OPENAI_API_KEY": "maestro-no-auth"
  }
  ```
  With these set, `CodexMaestro._build_register_mcp_servers_command()` writes the provider toml (verified inside `actix__actix__554` smoke trial: `model_provider = "agent-maestro"`, `wire_api = "responses"`, `requires_openai_auth = false`); harbor's `CodexAgent` upstream code reads `CODEX_FORCE_API_KEY=1` and forwards `OPENAI_API_KEY` into the container. The rerun shows full agent loops (e.g. octokit/plugin-paginate-rest.js trial: 50 command executions + 2 file edits).
- **Lesson for future codex configs**: any agent that relies on a custom provider must declare the required env vars explicitly in `agent.env` of the run config; do not depend on host environment unless documented. Consider adding a preflight assertion to the `CodexMaestro` shim that raises if `CODEX_MAESTRO_BASE_URL` is unset.

**Headline takeaways:**

1. **Agent harness dominates model choice on this benchmark.** Same `gpt-5.5`, copilot beats codex by 9.7 pp (36.8 % vs 27.1 %). That is the same delta we previously observed for copilot's default model vs codex (37 % vs 33 % on prior v3 runs), so the gap is genuine and reproducible.
2. **`gpt-5.5` boosts copilot by 9.7 pp** over copilot's default-model v3-155 run (27.1 % → 36.8 %); the model upgrade is real and stacks on top of harness quality.
3. **`gpt-5.5` does not help codex** vs codex's prior gpt-5.5 v3-191 run (36.6 %) — the difference here is the dataset prune (37 fewer "easy" / unfair tasks) plus the minimal-instruction format, which together drop codex by ~9 pp. The minimal instruction may matter more for codex than for copilot (copilot is robust to it, codex isn't); this remains untested directly and is the most likely follow-up A/B.
4. **No "agent claimed pass but FAILED" issue this round** — both agents had 0/x such rows under the heuristic, confirming the prune+minimal-instruction policy removed most pathologically-misleading tasks.
5. **Failure mode is overwhelmingly `assertion_failure`** for both (80 of 93 copilot FAILs; 92 of 110 codex FAILs) — the genuine hold-out test mechanism is now what the benchmark actually measures, not infra noise.

**Per-task analyses (5 sheets each):**

- `copilot_gpt55_v3_full155_per_task_analysis.xlsx`
- `codex_gpt55_v3_full155_per_task_analysis.xlsx`

**Configs:**

- `_run_configs/copilot_cli_gpt55_v3_full155_2026-05-15__07-50-00.json`
- `_run_configs/codex_gpt55_v3_full155_2026-05-16__13-50-00.json` (fixed env)
- The earlier broken `_run_configs/codex_gpt55_v3_full155_2026-05-15__07-50-00.json` is preserved as an artifact alongside the broken job dir (`harbor_jobs/codex_gpt55_v3_full155_2026-05-15__07-50-00/`).

### v3-baseline pruned to 155 + minimal instructions (2026-05-14 → 2026-05-15)
- **Dataset**: **155 tasks** (192 → 155). Dropped 37 tasks where (a) `test_patch` is small (≤10 changed lines) AND contains no textual reference to any upgraded package name, AND (b) v2 verifier already failed. These were drive-by changes in the original PR (assertion-string casing tweaks, lint touch-ups, lockfile-hash diffs unrelated to the dependency upgrade). Authoritative example: `auth0__go-auth0__348` — `test_patch` only changes one assertion `"Unsupported algorithm"` → `"unsupported algorithm"`, totally unrelated to the `golang.org/x/oauth2 0.16.0 → 0.17.0` upgrade. Selection script: `_test_patch_unrelated_failed_v2.csv` (script logic in `_gen_per_task_analysis.py` ad-hoc + see commit message of `e33976a`). Backup parquet kept as `pass_dataset_clean.pre_drop_unrelated.parquet`.
- **Instruction minimization (155/155)**: every `instruction.md` rewritten to the absolute minimum the agent needs:
  ```
  <!-- harbor-canary GUID ... -->
  <!-- v3-no-manifest-preapply -->

  Bumps `<pkg>` from <from> to <to>.

  ## Constraints

  - **Do not modify any test files.** The test suite is the evaluation oracle and will be re-applied verbatim before grading.
  - Restrict your changes to the project's source code so that the existing tests pass against the upgraded dependency.
  ```
  Removed: Context paragraph, Working Directory hint, Upstream Release Notes / full PR body / commits, Dependabot footer. Rationale: these were prompt scaffolding that biased agents toward dependabot-style fixes; v3 baseline now measures the agent's intrinsic ability to discover the work needed.
- **`pass_dataset_clean.parquet`**: now also carries an `instruction` column (155 rows, self-contained — no need to read `harbor_benchmark/tasks/<f>/instruction.md` separately).
- **Branch**: `v3-no-manifest-preapply` commit `e33976a` (`v3: prune 37 unrelated-test_patch tasks; minimize instructions to bumps+constraints`).
- **Result — copilot-cli (1.0.42)**: **42 PASS / 104 FAIL / 9 ERR → 27.1 %** (mean reward 0.276; ex-infra: 28.8 %).
  - By eco: cargo 3 / 10 (30.0 %) · pip 6 / 18 (33.3 %) · go_modules 13 / 35 (37.1 %) · npm_and_yarn 20 / 92 (21.7 %)
  - vs v2-192 copilot (28.6 %): −1.5 pp overall; npm/yarn −5.8 pp (manifest auto-generation harder), go +8.2 pp (data cleaner), cargo −24.5 pp (N=10, sample noise)
  - "Agent claimed success but FAILED" = **54 / 104 = 52 %** (vs v2's 64 %) — pruning eliminated some unfair hold-out cases but the dominant failure mode is unchanged: agent satisfies *visible* old tests, verifier swaps in *hidden* new tests.
  - Top FAIL root_causes: assertion_failure 85 · typescript_compile_error 9 · missing_module_or_path 7 · agent_timeout 6.
  - Top ERR error_locations: agent loop time-budget exceeded 6 · UnknownException 2 · agent non-zero exit 1.
- **Copilot-cli GLIBC fix (kept from prior session)**: all 13 `_run_configs/copilot_cli_*.json` pin `kwargs.version = "1.0.42"`. Newer copilot-cli pkg ships `runtime.linux-x64-gnu.node` requiring GLIBC ≥2.33; harbor task base images run Debian 11 (glibc 2.31). v1.0.42 lacks that native module and works.
- **Job dir**: `harbor_jobs/copilot_cli_v3_full155_2026-05-14__11-30-00/`
- **Run config**: `_run_configs/copilot_cli_v3_full155_2026-05-14__11-30-00.json`
- **Per-task analysis**: `copilot_cli_v3_full155_per_task_analysis.xlsx` (Summary + All_155 + PASS_42 + FAIL_104 + ERR_9 with `folder, ecosystem, status, upgrade_summary, agent_action, root_cause, error_location, url`).
- **Pending under this baseline**: codex × v3-155 not yet run; v2-baseline branch not yet synced to the 155 prune (so the 4-way matrix table will need a v2-155 re-run before final share-out).

### v2 dataset finalization — 192 oracle-validated tasks (2026-05-12)
- **End state**: `harbor_benchmark/tasks/` and `pass_dataset_clean.parquet` both hold **192 tasks**, every one of which has been independently oracle-validated (oracle applies the trio `manifest.patch → code.patch → test.patch` and runs `test_state.py`; reward must be 1.0).
- **How we got here**:
  1. Took the prior 191-task v2 baseline (post `_rescue_v2` cleanup) and ran oracle three times after refetching diffs from GitHub. Best-of: 146 PASS / 40 FAIL / 5 EXC = 76.4 %.
  2. **Phase 1 — drop**: removed the 40 FAIL + 5 EXC tasks (real env or data bugs, not flakes). Folders moved to `_v2_dropped_2026-05-12/`. Result: 146 tasks.
  3. **Phase 2 — mine clean/minor_drive_by from `pass_dataset.parquet`** (the broader pool of 330 PR candidates): 41 candidates rebuilt with `convert_to_harbor.py` + refetched via `_run_configs/refetch_split.py`; oracle yielded 24 PASS / 9 FAIL / 8 EXC. Non-PASS dropped to `_phase2_dropped_2026-05-12/`. Result: 170 tasks.
  4. **Phase 3 — mine mixed-purity from `pass_dataset.parquet`**: 56 candidates, 3 oracle rounds at progressively lower concurrency to absorb docker flakes. Best-of: 22 PASS / 9 FAIL / 24 EXC + 1 lost trial. Result: **192 tasks**.
- **Test-path classifier (now correct)**: `_run_configs/refetch_split.py` recognises as test paths: `tests?/`, `__tests__/`, `spec/`, `e2e/`, `regression/`, `integration-tests?/`, `unit-tests?/`, **`testdata/`, `fixtures?/`, `__fixtures__/`, `__mocks__/`, `cypress/`, `playwright/`, `conftest/`**, plus filename patterns `test_*.py`, `*_test.{py,go,rb}`, `*.test.*`, `*.spec.*`, `*Test.java`, `*Tests.cs`, `conftest.py`. The added `testdata/__fixtures__/__mocks__` patterns fix a remaining leak found in 8 v2 tasks (33 fixture files lived in `code.patch` instead of `test.patch`; surgically moved via `_test_misclass_fix_2026-05-12/` backup) — agent never sees these hidden fixtures during a run.
- **Manifest classifier**: `MANIFEST_RE` includes `go.work` and `go.work.sum` (added during v2 validation when `ymtdzzz__otel-tui__153` mis-routed `go.work.sum` into `code.patch`).
- **Final ecosystem mix (192)**: npm_and_yarn 102 / go_modules 45 / pip 34 / cargo 11. More balanced than the 146-task interim state (npm 81 / go 39 / pip 17 / cargo 9).
- **Drop tallies (mining phases)**:
  - Phase 2 dropped 17: 9 oracle-FAIL (tests really fail with the canonical patch); 8 EXC (Dockerfile env bugs — EOL Debian Stretch, `--frozen-lockfile` lockfile drift, yarn build failures, etc).
  - Phase 3 dropped 34: 9 oracle-FAIL; 24 EXC (mostly Dockerfile env bugs: 4× freqtrade pip-install, dependabot-core base image apt-repo rot, git-clone exit 128, node-sass build failures); 1 lost trial.
- **Artifacts**:
  - `pass_dataset_clean.parquet` — 192 rows; columns same as pre-v2 (no `oracle_v2_status` / `benchmark_known_broken` flags anymore — everything left is PASS).
  - `harbor_benchmark/task_summary.json` — regenerated index (192 rows, all with parsed library/old/new versions).
  - `_phase2_dropped_2026-05-12/`, `_phase3_dropped_2026-05-12/`, `_v2_dropped_2026-05-12/` — full archive of dropped task dirs + pre-drop parquet backups.
  - `_phase2_refetch_backup_2026-05-12/` — pre-refetch patch backups for the 41 phase-2 candidates.
  - `_test_misclass_fix_2026-05-12/` — pre-reclass code/test.patch backup for the 8 affected v2 tasks.
  - Oracle job dirs retained: `harbor_jobs/oracle_v2_refetched_2026-05-12__03-00-00`, `..._retry_2026-05-12__04-30-00`, `oracle_v2_test_reclass_2026-05-12__06-00-00`, `oracle_v2_phase2_2026-05-12__07-30-00`, `..._retry/_retry2`, `oracle_v2_phase3_2026-05-12__08-15-00`, `..._retry/_retry2`.
- **Implication for prior agent scores**: previous copilot v2 (66/191) and codex v2 (75/191) numbers were against the **truncated** 191-task pre-clean dataset. With the 192-task validated dataset all four agent×variant scores need rerun before share-out.

### Oracle v2 validation — re-fetched dataset (2026-05-12)
- **Goal**: validate that the v2 task patches (`manifest.patch` + `code.patch` + `test.patch`) reproduce each PR's effect end-to-end (oracle = applies code.patch then runs tests; expected reward=1.0 on every task)
- **Sequence of three oracle runs**:
  1. **Initial (existing clean dataset)** `harbor_jobs/oracle_v2_2026-05-11__02-30-00/` → **84 PASS / 107 FAIL / 0 EXC = 44.0%**
  2. **Restored from `pass_dataset.parquet`** (pre-`_rescue_v2` cleanup) `oracle_v2_restored_2026-05-11__07-50-00/` → **128 PASS / 47 FAIL / 16 EXC = 67.0%**
  3. **Re-fetched fresh from GitHub `.diff`** with pure-path classifier (`_run_configs/refetch_split.py`) → `oracle_v2_refetched_2026-05-12__03-00-00/` + retry on FAIL/EXC `oracle_v2_refetched_retry_2026-05-12__04-30-00/` → **best-of: 146 PASS / 40 FAIL / 5 EXC = 76.4%**
- **Root cause identified**: `_rescue_v2/lib_diff.py::clean_patch()` (used to produce `pass_dataset_clean.parquet`) dropped hunks/files that didn't literally mention package keywords. 87/191 (45%) tasks had `code.patch` files removed during that step — most often the real API-migration source files (e.g. `actix__actix__554` lost `actix-derive/src/{lib,message}.rs`, the syn 1→2 adapter code). When `upgraded_pkgs=[]` (18 tasks) or when keyword-heuristic mismatched (78 tasks), unrelated_files were silently zeroed.
- **Fix applied**: refetch every PR's `.diff` from `https://github.com/{repo}/pull/{N}.diff` and re-split using ONLY file-path classification (manifest = lockfile/package-manifest basenames; test = `(tests?|__tests__|spec|e2e)/` paths or `*test*`/`*spec*` filenames; code = everything else). No keyword filtering. Backup of overwritten patches in `_refetch_backup_2026-05-12/`.
- **40 remaining FAIL**: tagged as benchmark-known-broken in `pass_dataset_clean.parquet` via new columns `oracle_v2_status` and `benchmark_known_broken`. Listed with root_cause in `oracle_v2_final_report.xlsx` (KnownBroken_FAIL sheet). Not disabled — kept in dataset as ground-truth signal.
- **5 EXC**: docker-compose flakes (8GB OOM / build network); not a data bug.
- **Implication for earlier scores**: copilot v2 (66/191) and codex v2 (75/191) reported earlier ran against the **truncated** dataset. Some PASSes may have been agent-recovery-from-incomplete-patch (49 cases observed in slot "agent PASS / oracle FAIL"). **Final agent scores will need a re-run on the refetched dataset before sharing on 2026-05-11.**
- **Artifacts**:
  - `oracle_v2_final_report.xlsx` — Summary + All_status (color-coded) + KnownBroken_FAIL
  - `_run_configs/refetch_split.py` — refetch + path-classifier pipeline
  - `_run_configs/oracle_v2_refetched_2026-05-12__03-00-00.json` — first oracle run config
  - `_refetch_backup_2026-05-12/` — pre-refetch patch backups
  - Tagged columns in `pass_dataset_clean.parquet`: `oracle_v2_status`, `benchmark_known_broken`

### codex (gpt-5.5) — v2 baseline (2026-05-10 03:16 UTC)
- **Dataset**: 191 tasks (post hunk-cleanup, same as copilot v2)
- **Agent**: `codex-cli 0.130.0` via custom `CodexMaestro` subclass (`_run_configs/codex_maestro_agent.py`); routed through local Agent Maestro proxy at `http://172.100.216.1:23333/api/openai/v1` (`wire_api = "responses"`, `requires_openai_auth = false`); model `gpt-5.5`, default `model_reasoning_effort = high`
- **Concurrency**: 4
- **Resource per trial**: 2 cpu / 8 GB RAM / 20 GB disk; agent 1800s, verifier 300s, build 900s
- **Result**: **75 PASS / 115 FAIL / 1 ERR → 39.3 %** (vs copilot v2 34.6 %, **+4.7 pp**)
  - By eco: cargo 6/9 (66.7 %); pip 10/26 (38.5 %); go_modules 24/55 (43.6 %); npm_and_yarn 35/101 (34.7 %)
  - Codex strengths over copilot v2: go_modules (+10.9 pp), npm/yarn (+3.5 pp); ties on cargo and pip
  - Only 1 ERR (vs copilot's 23) — codex with `responses` wire_api essentially never times out at 30 min
- **Job dir**: `harbor_jobs/codex_v2_2026-05-10__03-16-01/` (per-task `_aggregate.csv` inside)
- **Run config**: `_run_configs/codex_v2_2026-05-10__03-16-01.json`
- **Per-task / cross-agent diffs**: `four_way_codex_vs_copilot_v2_v3.xlsx`

### codex (gpt-5.5) — v3 (no manifest pre-apply) (2026-05-09 04:59 UTC)
- **Dataset**: 191 tasks; same harness as copilot v3 (`v3-no-manifest-preapply` branch — manifest/lock files NOT pre-applied; agent must produce them)
- **Agent / model / proxy**: same `CodexMaestro` setup as codex v2
- **Concurrency**: 4; elapsed 9h 46m
- **Result**: **70 PASS / 116 FAIL / 5 ERR → 36.6 %** (vs copilot v3 33.0 %, **+3.6 pp**)
  - By eco: cargo 5/9 (55.6 %); pip 8/26 (30.8 %); go_modules 17/55 (30.9 %); npm_and_yarn 40/101 (39.6 %)
  - **Manifest preapply effect (v2 → v3)**: codex −2.7 pp (75 → 70); copilot −1.6 pp (66 → 63). Both agents lose accuracy when forced to author manifest+lock themselves.
  - **Notable regression**: codex go_modules drops 24 → 17 (−12.7 pp eco) — biggest single (agent×eco) regression in the four-way matrix
- **Exceptions**: 5 (mostly `AgentTimeoutError` at 1800s on heavy npm tasks still running tests)
- **Job dir**: `harbor_jobs/codex_v3_2026-05-09__04-59-48/`
- **Run config**: `_run_configs/codex_v3_2026-05-09__04-59-48.json`
- **Per-task diffs**: `codex_vs_copilot_v3_diff.xlsx`, `four_way_codex_vs_copilot_v2_v3.xlsx`

### v3 — copilot-cli, no manifest pre-apply (2026-05-07 03:30 UTC)
- **Dataset**: 191 tasks (same as v2)
- **Agent**: copilot-cli (default model)
- **Branch**: `v3-no-manifest-preapply` — `solution/manifest.patch` is NOT applied at build time; agent must write the manifest+lock changes itself in addition to source-code adaptations. `code.patch` (source/test fixes) still hidden.
- **Concurrency**: 4
- **Result**: **63 PASS / 113 FAIL / 15 ERR → 33.0 %** (vs v2 34.6 %, **−1.6 pp**)
  - By eco: cargo 4/9 (44.4 %); pip 5/26 (19.2 %); go_modules 19/55 (34.5 %); npm_and_yarn 35/101 (34.7 %)
  - Pip drops sharpest (35.7 % → 19.2 %): authoring `requirements.txt` / `pyproject.toml` from scratch is significantly harder than editing pre-applied manifest
  - npm/yarn slightly improves (+7.5 pp) — copilot is comfortable running `yarn upgrade` end-to-end
- **Job dir**: `harbor_jobs/copilot_cli_v3_2026-05-07__03-30-00/`
- **Run config**: `_run_configs/copilot_cli_v3_2026-05-07__03-30-00.json`
- **Per-task analysis**: `copilot_cli_v3_per_task_analysis.xlsx` (5 sheets incl. v2 vs v3 diff)

### v2 — clean dataset + watchdog/uvx-PATH fix (2026-05-04 15:32 UTC)
- **Dataset**: **195 tasks** (218 → 195)
  - Dropped 10 infra-unfixable (db_service / dns_flaky / subprocess_hang / missing_build_artifact / other) → `_drop_infra_unfixable_20260504_150821/`
  - Dropped 13 bad_test_confirmed (oracle missing capability / test contradicts reality / unfixable test.patch) → `_drop_bad_test_20260504_151850/`
- **Agent**: copilot-cli (default model)
- **Concurrency**: 6
- **Resource per trial**: 2 cpu / 8 GB RAM / 20 GB disk; agent 1800s, verifier 300s, build 900s
- **Harness fixes vs v1.1**:
  - **`watchdog.sh`** threshold raised from 10 min → 60 min. Old regex `[1-9][0-9]+` matched any container ≥10 min and SIGKILL'd it (exit 137 = `NonZeroAgentExitCodeError`). All long-running legit agents were being murdered. New regex: `(6[0-9]|[7-9][0-9]|[1-9][0-9]{2,}) minutes|hour`.
  - **uvx PATH isolation fix** in 14 pip-bucket `tests/test_state.py`: injected `env={**os.environ, "PATH": "/usr/local/bin:/usr/bin:/bin:" + os.environ.get("PATH","")}` into `subprocess.run(...)`. Without this, the inner `python -m pytest` was resolved to `uvx pytest`'s ephemeral venv (which lacks the project deps), producing spurious `ModuleNotFoundError`. Backups in `_infra_fix/uvx_path_fix_backup/`.
  - 28 infra_fix28 Dockerfile patches from `_infra_fix/` retained.
- **Result** (195/195 aggregated via `config.json["task"]["path"]` — earlier 190/195 number was a slug-prefix-matching bug in the aggregator): **62 PASS / 110 FAIL / 23 ERR → 31.8 %** (after 4 post-run infra fixes + 2026-05-06 label audit promoting 3 ERR with `reward=1.0` to PASS; pre-audit: 59/110/26 = 30.3 %; pre-fix: 58/110/27 = 29.7 %)
  - All ERR are now genuine `AgentTimeoutError` (30-min hit). Zero spurious watchdog kills (was 12+ in v1.1 / infra_fix28).
  - Pip tasks previously stuck on `ModuleNotFoundError` now run real test suites and either PASS legitimately or FAIL with real assertion errors (e.g. `iterative__dvc__7899`: 19 passed, 2 failed).
- **Post-run infra fixes (2026-05-05, 5 rounds)**: 4 tasks had genuinely-missing infra masking the real agent outcome. Patches in `_infra_fix/v2_post_run_fixes.md`. After fixes:
  - `hoelsner__product-database__36`: ERR → **PASS** (added `postgresql-client`; agent's MockSession patch now applies cleanly)
  - `mozilla__experimenter__10256`: FAIL → FAIL (added 50+ env vars incl. `LOG_FORMAT=text`, all decouple errors gone; remaining 13 errors are real test-suite issues)
  - `onicagroup__runway__1979`: FAIL → FAIL (added `pytest-mock` to both poetry venv & system, PATH→`/app/.venv/bin` first; agent's patch now rejects on real test files)
  - `webhintio__hint__4027`: FAIL → FAIL (added `npm install -g --force cpx@1.5.0`; original cpx-not-found resolved, remaining is TypeScript build error in agent's upgrade)
  - **Dataset sync (2026-05-06)**: 4 fixed Dockerfiles written back to `pass_dataset_clean.parquet` (`dockerfile` column). Backup: `pass_dataset_clean.parquet.bak_pre_v2_infrafix4_*`.
  - **Label audit (2026-05-06)**: systematic verification of all 195 rows in `copilot_cli_v2_per_task_analysis.xlsx` against ground-truth (jsonl edit count, last assistant message, `verifier_result.rewards`). Findings: (a) 3 tasks with `AgentTimeoutError` had `reward=1.0` and are now correctly classified as PASS (`bbc__psammead__3709`, `aws__aws-sdk-pandas__2883`, `cloudant__nodejs-cloudant__400`); (b) 21 FAIL rows previously labeled `agent_wrong_change`/`agent_partial_fix` had 0 edits — relabeled to `agent_no_change`; (c) 6 ERR labeled `infra_residual` had no missing-tool patterns — re-classified to `agent_timeout`/`agent_partial_fix`. Net: +3 PASS, -3 ERR.
  - **Infra fix #5 — `wayfair-incubator__pygitops__272` (2026-05-06)**: per-task verdict review of the 23 `agent_no_change` FAIL surfaced a real benchmark data bug: verifier ran `pytest -p no:cacheprovider --no-cov` from inside a uvx ephemeral env that had no `pytest-cov` plugin (so `pytest.ini`'s `addopts=--cov=pygitops --cov-report term-missing` was unparseable, exit code 4) AND no project runtime deps (`filelock`, `GitPython`). Fix: `tests/test.sh` now uvx-installs `pytest-cov==3.0.0` + `pytest-mock==3.10.0`, and `tests/test_state.py` invokes the project's `/usr/local/bin/python -m pytest` so subprocess sees the pip-installed deps. Also discovered the `solution/code.patch` was incomplete — missing `pygitops/exceptions.py` (`PyGitOpsWorkingDirError` definition) and `pygitops/operations.py` chunks; regenerated from upstream PR 272. Oracle now PASS (reward=1.0); copilot-cli still FAIL (0 edits, agent claimed pass, real test signal `cannot import name 'repo_working_dir'`). Net status unchanged for v2 (still FAIL `agent_no_change`); but the task is now scientifically-valid for any future re-runs.
  - Net: **+1 PASS, -1 ERR**. Verified job dirs: `harbor_jobs/copilot_cli_v2_infrafix4_2026-05-05__05-52-00.round{1..4}/` and final `.../copilot_cli_v2_infrafix4_2026-05-05__05-52-00/`.
  - **Hunk-level cleanup of false-positive verifiers (2026-05-06)**: per-task audit of the 22 `agent_no_change` FAIL cases (after pygitops fix) cross-checked the `tests/test.patch` against the upstream PR scope. Found 8 cases where `test.patch` contained hunks unrelated to the dep upgrade (drive-by lint/format/feature changes that broke even with no agent action). Backed up all 22 to `_hunk_cleanup_2026-05-06/backup/`, then emptied the 8 invalid `test.patch` files. Oracle re-run results: 4 task PASS (`chris48s__v8r__22`, `octokit__auth-oauth-app.js__137`, `oceanprotocol__market__1687`, `qntm__base65536__49` — verifier was the only failure source); 4 still FAIL because of deeper structural contamination (manifest empty + dep change misplaced in `code.patch`, drive-by source bumps unrelated to any dep, or workspace-build infra issues): `pypa__warehouse__7826`, `peopledatalabs__peopledatalabs-python__132`, `microsoft__accessibility-insights-service__2137`, `m-h-c-t__mh-helper-extension__434` — these 4 are **moved to `tasks_disabled_contam/<task>.invalid_2026-05-06`** (cannot be repaired without rewriting the task generator). Re-ran copilot-cli on the 4 cleaned PASS tasks (`harbor_jobs/copilot_cli_v2_hunk_cleanup_2026-05-06/`): all 4 score **reward=1.0** (agent's no-action is now correctly rewarded). Net for v2: **denominator 195 → 191; PASS 62 → 66**; final score **66/191 = 34.6 %** (vs 31.8 % pre-cleanup).
- **By ecosystem** (post-audit):
  - cargo: 6 / 9 = **66.7 %**
  - pip: 10 / 28 = **35.7 %**
  - go_modules: 18 / 55 = **32.7 %**
  - npm_and_yarn: 28 / 103 = **27.2 %**
- **Job dir**: `harbor_jobs/copilot_cli_v2_2026-05-04__15-32-00/` (per-task `_aggregate.csv` inside)
- **Run config**: `_run_configs/copilot_cli_v2_2026-05-04__15-32-00.json`
- **Comparison vs v1.1 (218 → 195, 30.3 % → 29.7 %)**: PASS rate basically unchanged but on a *clean* denominator (no watchdog noise, no oracle-broken tests, no uvx isolation artifacts). v2 is the trustworthy baseline going forward.

### v1.1 — infrastructure-clean stitched (2026-04-29 09:00 UTC)
- **Dataset**: 218 tasks (68 original + 150 rescued)
  - Dropped from v1: 15 trivial PDL (version-only tests) + 2 dead base_sha + 9 unrescuable (lockfile/yanked/external-DB) + 4 GLIBC-incompatible base images + 10 unfixable infra (toolchain/canary/timeout)
- **Agent**: copilot-cli (default model)
- **Concurrency**: 6 (initial v1) + 4 (subsequent ERR retries)
- **Dockerfile fixes applied** (all rebuild dirs):
  - `USER root` + Debian buster/bullseye `archive.debian.org` redirect with EOL `-security/-updates/-backports` lines stripped
  - 4 LLM-generated `FROM` syntax fixes (parenthetical comments removed)
  - Per-task: rustup install (commonmarker), setup-envtest install (karpenter), drop lerna build (ai-service), drop `--require-hashes` (gcp-ingestion), pin Node 14 (raiden), loosen ray pin (raylab), nodejs install in dotnet image (heroicons)
  - **Memory bump**: `override_memory_mb=8192` (recovered 2 OOM cases)
- **Result merging**: per-folder LATEST job result stitched across v1 + 3 ERR retries
- **Result**: 66 PASS / 152 FAIL / **0 ERR** → **30.3 %**
  - Rescued: 46 / 104 / 0 → **30.7 %**
  - Original: 20 / 48 / 0 → **29.4 %**
- **Source jobs**:
  - `harbor_jobs/copilot_cli_rescue258_2026-04-28__03-38-08/` (original full run)
  - `harbor_jobs/copilot_cli_err_retry32_2026-04-29__03-29-32/` (mem bump, max_retries=2)
  - `harbor_jobs/copilot_cli_err_retry23_2026-04-29__06-04-59/` (Dockerfile fixes v1)
  - `harbor_jobs/copilot_cli_err_retry19_2026-04-29__06-51-52/` (Dockerfile fixes v2 — bullseye-security strip)
- **Drop backups**: `_drop_pdl_trivial_*`, `_drop_dead_base_sha_*`, `_drop_unrescuable_*`, `_drop_glibc_*` (parquet+csv+task dirs)

### v1 — first rescued run (2026-04-28 03:38 UTC)
- **Dataset**: 258 tasks (83 original + 175 rescued via `_rescue_v2/`)
- **Agent**: copilot-cli (default model)
- **Concurrency**: 6
- **Manifest pre-applied**: yes (build-time)
- **Test patch**: hidden, applied at verify-time
- **PR body in instruction**: yes (cleaned, max 4 KB)
- **Resource per trial**: 2 cpu / 4 GB RAM / 20 GB disk
- **Timeouts**: agent 1800s, verifier 300s, build 900s
- **Result**: 67 PASS / 157 FAIL / 34 ERR → 26.0 % (rescued 25.7 %, original 26.5 %)
- **Job dir**: `harbor_jobs/copilot_cli_rescue258_2026-04-28__03-38-08/`

### v0 — clean83 baseline (2026-04-27 15:24 UTC)
- **Dataset**: 83 original
- **Agent**: copilot-cli
- **Concurrency**: 4
- **Result**: 16 PASS / 65 FAIL / 2 ERR → 19.3 %
- **Job dir**: `harbor_jobs/copilot_cli_clean83_prbody_2026-04-27__15-24-51/`

<!-- next variant template:
### v2 — <date> — <one-line description of what changed>
- **Dataset**: …
- **Agent / model**: …
- **Concurrency**: …
- **Other changes vs v(N-1)**: …
- **Result**: …
- **Job dir**: …
-->
