# Handoff: CloudGPT Token + OpenCode Chat Completions

Date: 2026-06-27

Summary:
- Simplified the Azure/CloudGPT auth work to a token helper and small OpenCode provider tweak.
- `scripts/with_cloudgpt_token.sh` refreshes a CloudGPT AAD token with `az account get-access-token` and exports it as `CLOUDGPT_OPENAI_TOKEN`, `OPENAI_API_KEY`, `CODEX_API_KEY`, and `AZURE_OPENAI_API_KEY`.
- `custom_agents/opencode.py` now auto-registers non-`openai`, non-`github-copilot` providers with a configured `base_url` as `@ai-sdk/openai-compatible`, using `OPENAI_API_KEY`. This lets `default_provider: cloudgpt` use OpenCode's chat-completions route instead of the built-in OpenAI Responses route.
- `configs/deepseek_v4_pro_cloudgpt_codex_opencode.yaml` sets OpenCode `default_provider: cloudgpt` and CloudGPT base URL.

Validation:
- `uv run python -m py_compile custom_agents/opencode.py custom_agents/codex.py` passed.
- `JobConfig.model_validate(yaml.safe_load(...))` passed for `configs/deepseek_v4_pro_cloudgpt_codex_opencode.yaml`.
- Direct OpenCode local smoke passed:
  - `OPENCODE_CONFIG_CONTENT=... scripts/with_cloudgpt_token.sh -- opencode --print-logs --log-level DEBUG --model=cloudgpt/DeepSeek-V4-Pro run --format=json -- "Return exactly OK."`
  - Output included a text event with `OK`.

Important details:
- The earlier OpenCode Harbor failure was not a true rate limit. OpenCode's built-in `openai` provider sent `/responses` with `input`; CloudGPT returned HTTP 400 `unrecognized_request_argument: input`, and Harbor misclassified it because the response headers had `x-ratelimit-*`.
- Codex still cannot use this CloudGPT DeepSeek model directly because current Codex source only accepts `wire_api = "responses"`; `wire_api = "chat"` is explicitly removed.
- `/home/v-runzhihe/msr4agent/bridge/bridge.internal-gemini-chat.config.json` is chat-only. Current bridge docs/code show `/v1/responses -> chat upstream` is not implemented; `/v1/responses` requires provider api `responses` and otherwise returns 501. The bridge already supports the opposite direction: `/v1/chat/completions -> responses upstream`.

Likely next command for OpenCode only:
`scripts/with_cloudgpt_token.sh -- uv run harbor run -c <opencode-only-config> -y`

If continuing, either create an OpenCode-only config or remove/comment the Codex agent from the current smoke config before running a Harbor smoke.
