# Claude Code 219-task gap diagnosis and hard14 launch

## What happened

- Current branch/dataset is `v4-with-test` with 219 task directories and 219 `task_summary.json` rows.
- The Claude Code Maestro configs that were run on 2026-06-23 were explicitly clean205 configs:
  - `_run_configs/claude_code_maestro_20260623/task_names_clean205.json`
  - `_run_configs/claude_code_maestro_20260623/claude_code_maestro_gpt55_clean205.json`
  - `_run_configs/claude_code_maestro_20260623/claude_code_maestro_gemini35flash_clean205.json`
- Therefore the pushed Claude Code totals are 205, not 219. This was a config-scope mistake: clean205 was run on the current v4-with-test branch instead of the full 219-task snapshot.

## Missing hard14 tasks

The 14 current tasks absent from the clean205 Claude configs are:

- `BramVR__gohealthcli__351`
- `Nextdoor__vigil__35`
- `giantswarm__mcp-prometheus__165`
- `giantswarm__muster__751`
- `github__github-mcp-server__412`
- `matt-riley__hopcli__47`
- `score-spec__score-aca__16`
- `shuntaka9576__gh-kanban__16`
- `stackitcloud__stackit-cert-manager-webhook__94`
- `syou6162__times_esa_mcp_server__22`
- `thegeeklab__wp-docker-buildx__349`
- `thegeeklab__wp-opentofu__166`
- `ubugeeei-prod__ox-content__131`
- `xMoelletschi__renoglaab__30`

## Fix started

- Added hard14-only configs under `_run_configs/claude_code_maestro_20260624/`.
- Launched Claude Code GPT-5.5 hard14:
  - Config: `_run_configs/claude_code_maestro_20260624/claude_code_maestro_gpt55_hard14.json`
  - Job: `harbor_jobs/claude_code_maestro_gpt55_hard14_conc5_2026-06-24__05-33-00`
  - Log: `_run_logs/claude_code_maestro_gpt55_hard14_conc5_2026-06-24__05-33-00.log`
- Startup check after ~70s:
  - total 14
  - completed 0
  - running 5
  - pending 9
  - errors 0

## Next

- Schedule #3 checks GPT-5.5 hard14 every 10 minutes.
- Once GPT-5.5 hard14 completes, schedule #3 should launch Gemini 3.5 Flash hard14.
- After Gemini hard14 completes, merge clean205 + hard14 into 219-task Claude Code summaries, update README, and push.
