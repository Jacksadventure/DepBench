# Task schema

Each benchmark task lives under `dataset/tasks/<task>/`.

## Files

| Path | Purpose |
|---|---|
| `instruction.md` | Prompt shown to the agent. |
| `task.toml` | Task metadata, resource limits, timeouts, and Docker image tag. |
| `environment/docker-compose.yaml` | Placeholder compose file; the task image is selected from `task.toml`. |
| `environment/patches/manifest.patch` | Dependency manifest upgrade patch used by the benchmark setup. |
| `solution/manifest.patch` | Oracle copy of the dependency manifest patch. |
| `solution/code.patch` | Oracle source-code repair patch. |
| `solution/solve.sh` | Applies the oracle repair inside the task container. |
| `tests/test.patch` | Hidden scoring test patch. |
| `tests/test.sh` | Verifier entry point. |
| `tests/test_state.py` | Verifier helper that applies `test.patch` and runs the task-specific test command. |

## Important `task.toml` fields

- `[environment].docker_image`: Docker image containing `/app`, the project checkout.
- `[environment].cpus`, `[environment].memory_mb`, `[environment].storage_mb`: resource metadata used by the benchmark.
- `[agent].timeout_sec`: maximum agent attempt time.
- `[verifier].timeout_sec`: maximum verifier time.
- `[metadata].tags`: ecosystem and dependency-upgrade labels.

## Scoring lifecycle

1. Start the task Docker image.
2. Give the agent `/app` and `instruction.md`.
3. Keep `solution/`, `tests/`, and `environment/patches/manifest.patch` hidden from the agent.
4. After the agent exits, mount `tests/` and run `tests/test.sh`.
5. Read `/logs/verifier/reward.txt`.

Reward is binary: `1` means the verifier passed, and `0` means it failed.
