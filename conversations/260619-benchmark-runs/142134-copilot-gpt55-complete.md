# Handoff — 142134 · copilot · gpt55-complete

## Context

The Copilot GPT-5.5 clean205 benchmark completed after three job segments:

- `copilot_cli_gpt55_clean205_reuse_host_auth_nopreapply_conc5_retry1_2026-06-20__00-15-00`
- `copilot_cli_gpt55_clean205_reuse_host_auth_resume124_conc5_2026-06-20__07-10-00`
- `copilot_cli_gpt55_clean205_reuse_host_auth_resume58_conc5_2026-06-20__11-28-00`

## Final aggregate

Across all three job dirs:

- 205 / 205 task folders have result files.
- 202 / 205 have verifier reward values.
- Rewards: 91 pass, 111 fail.
- Pass rate over reward-bearing tasks: 91 / 202 = 45.0%.
- Three task result files have no reward due to infrastructure interruption during the first stalled segment:
  - `geotools__geotools__4212`
  - `opentripplanner__OpenTripPlanner__5280`
  - `verdaccio__verdaccio__5742`

## Final resume58 job

`harbor_jobs/copilot_cli_gpt55_clean205_reuse_host_auth_resume58_conc5_2026-06-20__11-28-00/result.json` reports:

- `finished_at`: `2026-06-20T14:21:34.520945`
- 58 completed
- 2 errored
- 0 running
- 0 pending
- reward mean: 0.4827586206896552

## Docker status

Docker recovered after the full reset and was healthy at final check:

`client=29.5.3 server=29.5.3`

No Harbor benchmark runner remained active at final check.
