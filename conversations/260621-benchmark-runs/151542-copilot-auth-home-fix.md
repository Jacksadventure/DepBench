# Handoff — 151542 · copilot · auth-home-fix

## Context

- The Copilot + `gemini-3.5-flash` Harbor run launched at `2026-06-21__10-00-03` was producing mass `NonZeroAgentExitCodeError`.
- Root cause was not task-specific: Copilot CLI crashed before doing real work.

## Root cause

- The broken config mounted the whole host `.copilot` directory read-only at `/tmp/copilot-home` and set `COPILOT_HOME=/tmp/copilot-home`.
- Copilot 1.0.42 tries to create `session-state/<uuid>` inside `COPILOT_HOME`, so a read-only dir mount causes immediate startup failure:
  - `ENOENT: no such file or directory, mkdir '/tmp/copilot-home/session-state/<uuid>'`
- Evidence is in:
  - `harbor_jobs/copilot_cli_gemini35flash_v4_228_nopreapply_conc6_2026-06-21__10-00-03/*/exception.txt`
  - matching `agent/copilot-cli.jsonl` `session.error` payloads

## Fix applied

- Verified locally that Copilot works with:
  - a **writable** `COPILOT_HOME`
  - only `config.json` copied into that dir
- Verified with Docker that binding only the file
  - `/home/kszlzj/snap/copilot-cli/common/.copilot/config.json:/tmp/copilot-home/config.json:ro`
  still leaves `/tmp/copilot-home/` writable for `session-state/`.

## Files added/updated

- Added fixed Copilot run config:
  - `_run_configs/copilot_cli_gemini35flash_v4_228_nopreapply_conc6_2026-06-21__15-15-42.json`
- Updated queued watcher script:
  - `~/.copilot/session-state/428695ac-66d8-4922-a081-030abcc48818/files/queue_opencode_after_copilot.sh`
  - now waits for the new Copilot job name

## Process changes

- Stopped broken Harbor run PID `27125`
- Stopped stale watcher PID `193879`
- Relaunched fixed Harbor run:
  - PID `318422`
  - job dir `harbor_jobs/copilot_cli_gemini35flash_v4_228_nopreapply_conc6_2026-06-21__15-15-42/`
- Restarted OpenCode watcher:
  - watcher PID `318418`
  - monitor log `harbor_jobs/opencode_gemini35flash_v4_228_nopreapply_conc6_2026-06-21__12-37-23.monitor.log`

## Validation state

- New run no longer shows the old `/tmp/copilot-home/session-state` ENOENT/persistence failure.
- It is now emitting real Copilot JSONL output under trial dirs, including tool execution partial results, which confirms it gets past startup and into actual agent work.
- At last check the relaunched run had not yet finished a full trial, but it had 6 live trials and no immediate retries/errors.

## Important memory update

- Old repo memory about reusing Copilot auth by mounting `.copilot/config.json` and setting `COPILOT_HOME=/tmp/copilot-home` was downvoted because the unsafe interpretation was mounting the whole dir read-only.
- New correct memory stored:
  - use a writable `COPILOT_HOME`
  - bind-mount only `config.json` read-only into `$COPILOT_HOME/config.json`
