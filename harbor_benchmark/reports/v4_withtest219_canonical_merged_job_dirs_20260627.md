# Canonical merged Harbor job directories — v4-with-test219

Generated: 2026-06-27T06:32:13.628157+00:00

Implementation: symlink farm; original result dirs are unchanged.

Selection rule: Scan actual source job directories; for overlapping task trials choose success first, then reward-bearing, then newer source order, then newer mtime. Original job directories are unchanged.

Claude/Claude-4.8 current experiment directories are intentionally excluded.

| Agent | Model | Canonical job dir | Tasks | Pass | Fail | No reward | Source jobs |
|---|---|---|---:|---:|---:|---:|---|
| codex | gpt-5.5 | `v4_withtest219__codex__gpt55__merged_20260627` | 219 | 106 | 113 | 0 | `codex_cloudgpt_gpt55_clean205_nopreapply_conc5_2026-06-19__15-16-03`; `codex_cloudgpt_gpt55_clean205_resume204_clean_conc5_2026-06-21__04-12-00`; `codex_cloudgpt_gpt55_v4_with_test_added52_retry2_detached_conc10_2026-06-22__16-45-00`; `codex_cloudgpt_gpt55_v4_with_test_hard14_resume_conc10_2026-06-23__02-30-00` |
| copilot_cli | gpt-5.5 | `v4_withtest219__copilot_cli__gpt55__merged_20260627` | 219 | 98 | 118 | 3 | `copilot_cli_gpt55_clean205_reuse_host_auth_nopreapply_conc5_retry1_2026-06-20__00-15-00`; `copilot_cli_gpt55_clean205_reuse_host_auth_resume124_conc5_2026-06-20__07-10-00`; `copilot_cli_gpt55_clean205_reuse_host_auth_resume58_conc5_2026-06-20__11-28-00`; `copilot_cli_gpt55_v4_with_test_added52_retry2_detached_conc10_2026-06-22__16-45-00` |
| opencode | gpt-5.5 | `v4_withtest219__opencode__gpt55__merged_20260627` | 219 | 95 | 124 | 0 | `opencode_cloudgpt_gpt55_clean205_nopreapply_conc5_2026-06-19__15-16-03`; `opencode_cloudgpt_gpt55_v4_with_test_added52_retry2_detached_conc10_2026-06-22__16-45-00`; `opencode_gpt55_clean205_resume_after_codex_conc5_2026-06-21` |
| codex | gemini-3.5-flash | `v4_withtest219__codex__gemini35flash__merged_20260627` | 219 | 61 | 158 | 0 | `codex_maestro_gemini35flash_v4_withtest_219_conc10_2026-06-23__16-10-14` |
| copilot_cli | gemini-3.5-flash | `v4_withtest219__copilot_cli__gemini35flash__merged_20260627` | 219 | 49 | 169 | 1 | `copilot_cli_gemini35flash_v4_with_test219_gemini_only_conc10_2026-06-23__10-45-00` |
| opencode | gemini-3.5-flash | `v4_withtest219__opencode__gemini35flash__merged_20260627` | 219 | 38 | 181 | 0 | `opencode_gemini35flash_clean205_frozen_conc6_2026-06-22__03-11-12`; `opencode_gemini35flash_v4_withtest_new14_conc6_2026-06-23__10-42-23` |
