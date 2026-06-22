# Handoff — 173000 · copilot · host-auth-reuse

## Context

User wanted to reuse the currently authenticated host Copilot CLI for Harbor Copilot evaluation instead of creating a new fine-grained PAT.

## Finding

The host Copilot CLI has no `COPILOT_GITHUB_TOKEN`, `GH_TOKEN`, or `GITHUB_TOKEN` in the environment, but it authenticates from `~/.copilot/config.json`. Running Copilot with an empty `HOME` fails authentication, confirming the auth is in the Copilot home state.

Tested a clean Debian container with only this file mounted read-only:

```bash
docker run --rm \
  -v "$HOME/.copilot/config.json:/tmp/copilot-home/config.json:ro" \
  -e COPILOT_HOME=/tmp/copilot-home \
  debian:12 ...
```

After installing Copilot CLI 1.0.42 in that container, `copilot --prompt="Say ok only." --output-format=json --model=gpt-5.5` succeeded.

## Config generated

Generated:

`_run_configs/gpt55_clean205_20260619/copilot_reuse_host_auth.json`

Key settings:

- Mounts `/home/kszlzj/.copilot/config.json` read-only to `/tmp/copilot-home/config.json`.
- Sets agent env `COPILOT_HOME=/tmp/copilot-home`.
- Keeps Copilot CLI pinned to `version=1.0.42`.
- Uses the existing 205-task clean allowlist.

Launch command:

```bash
cd /home/kszlzj/DepBench
nohup ~/.local/bin/harbor run --config _run_configs/gpt55_clean205_20260619/copilot_reuse_host_auth.json \
  > _run_logs/copilot_cli_gpt55_clean205_reuse_host_auth_nopreapply_conc5_2026-06-19__17-30-00.log 2>&1 &
```

## Security caveat

This exposes the host Copilot OAuth credential file inside each agent container. The mount is only the single config file and is read-only, not the whole `~/.copilot` directory, but the file is still sensitive. A fine-grained PAT with only Copilot Requests remains the cleaner automation credential.
