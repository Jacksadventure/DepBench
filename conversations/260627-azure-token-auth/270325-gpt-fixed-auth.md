# Handoff Note — 270325 · gpt · fixed-auth

## 继承上下文

- 按 handoff Mode A 检查了最近线程；最新 `conversations/260626-harbor-job-retrieval/` 与本次 Azure token 认证不匹配，因此新建本线程。
- 额外阅读了 `conversations/260625-custom-agent-collector/` 中 custom agent 相关交接，确认现有约定：`custom_agents.codex:CustomCodex` 和 `custom_agents.opencode:CustomOpenCode` 已支持 `~/.claude/settings.json`、OpenAI-compatible gateway、artifact hook、OpenCode Copilot 模式。
- 读取了本机 `~/.codex/config.toml`，确认当前 provider 为 `copilot_api`，关键字段是 `base_url = http://10.12.1.193:40441`、`env_key = GITHUB_COPILOT_API_KEY`、`requires_openai_auth = true`、`wire_api = responses`。读取输出时已隐藏 token。

## 本次完成

- [x] 新增共享 helper `custom_agents/codex_config.py`，解析本机 Codex config/auth，并支持 Azure/CloudGPT AAD token fallback。
- [x] 扩展 `custom_agents/codex.py`，让 `CustomCodex` 可读取 `~/.codex/config.toml` 的 provider；新增 `AzureTokenCodex` 显式别名，默认优先本机 Codex provider。
- [x] 扩展 `custom_agents/opencode.py`，新增 `codex_provider` 模式与 `AzureTokenOpenCode` 别名，把 Codex provider 的 baseURL/token 映射到 OpenCode 的 `openai/<model>` provider 配置。
- [x] 新增单任务 smoke 配置：`configs/custom_codex_azure_token_smoke.yaml`、`configs/custom_opencode_azure_token_smoke.yaml`。
- [x] 完成语法、Harbor `JobConfig`、本机 provider 解析和 token 映射验证。

## 当前状态

| File | Change |
| ---- | ------ |
| `custom_agents/codex_config.py` | 新增；读取 `~/.codex/config.toml` / `auth.json`，规范化 Azure/OpenAI base URL，并可通过 `az account get-access-token` 获取 CloudGPT/AAD token。 |
| `custom_agents/codex.py` | 支持 `codex_config_path`、`codex_auth_path`、`env_key`、`prefer_codex_provider`、`azure_token_auth`；provider config 会写入 Codex CLI 的 `env_key` 和 `requires_openai_auth`；新增 `AzureTokenCodex`。 |
| `custom_agents/opencode.py` | 支持 `codex_provider`、`codex_provider_name`、`codex_config_path`、`codex_auth_path`、`azure_token_auth`；新增 `AzureTokenOpenCode`。 |
| `configs/custom_codex_azure_token_smoke.yaml` | 新增 Codex Azure-token 单任务 smoke。 |
| `configs/custom_opencode_azure_token_smoke.yaml` | 新增 OpenCode Azure-token 单任务 smoke。 |

验证命令已运行：

```bash
uv run python -m py_compile custom_agents/codex_config.py custom_agents/codex.py custom_agents/opencode.py custom_agents/claude_code.py custom_agents/copilot_cli.py custom_agents/hooks.py
uv run python - <<'PY'
import yaml
from pathlib import Path
from harbor.models.job.config import JobConfig
for name in [
    'configs/custom_codex_azure_token_smoke.yaml',
    'configs/custom_opencode_azure_token_smoke.yaml',
    'configs/custom_agents_smoke.yaml',
    'configs/custom_codex_smoke.yaml',
    'configs/custom_opencode_smoke.yaml',
]:
    cfg = JobConfig.model_validate(yaml.safe_load(Path(name).read_text()))
    print(name, len(cfg.agents), [a.import_path for a in cfg.agents])
PY
```

还运行了实例级断言，确认本机 provider 被解析为 `copilot_api`，env key 为 `GITHUB_COPILOT_API_KEY`，Codex/OpenCode alias 都会使用该 provider；token 检查只输出长度，没有输出 secret。

## 后续任务

1. 在 Docker/socket 状态确认后跑 smoke：
   `set -a; . ./.env; set +a; uv run harbor run -c configs/custom_codex_azure_token_smoke.yaml -y`
2. 再跑 OpenCode smoke：
   `set -a; . ./.env; set +a; uv run harbor run -c configs/custom_opencode_azure_token_smoke.yaml -y`
3. 检查对应 `harbor_jobs/...` 里 `agent/codex.txt` 或 `agent/opencode.txt`，确认没有认证错误，并检查 `artifacts/solution_patch.diff` 等 artifact 是否收集。
4. 如果要扩大到 clean205，先按 AGENTS.md 约定冻结 `harbor_benchmark/tasks_v4` 快照，不要直接指向 mutable working tree。

## 关键决策

| Decision | Rationale |
| -------- | --------- |
| 新增 `custom_agents/codex_config.py` 共享 helper | Codex 和 OpenCode 都需要读取同一份本机 Codex provider/token 约定，避免两处复制解析逻辑。 |
| `AzureTokenCodex` 默认 `prefer_codex_provider=True` | 用户明确要求参考本机 Codex 配置，不能被 `~/.claude/settings.json` 的旧代理配置抢优先级。 |
| OpenCode Azure-token 模式走 `openai/<model>` + `provider.openai.options.baseURL` | 这是之前已验证过的 OpenCode OpenAI-compatible 路径；比直接赌 OpenCode 原生 `azure` provider 的字段语义更稳。 |
| token 解析顺序包含 provider env_key、`CLOUDGPT_OPENAI_TOKEN`、`GITHUB_COPILOT_API_KEY`、`AZURE_OPENAI_API_KEY`、`auth.json`、`az login` | 兼容当前本机 `GITHUB_COPILOT_API_KEY` 配置，也兼容旧 CloudGPT/Azure 命名。 |

## 阻塞

- 未运行真实 Harbor smoke；本会话只做了本地语法、配置和 provider/token 映射验证。真实 smoke 依赖 Docker/socket 当前可用状态。

## 建议下一步

先跑 `configs/custom_codex_azure_token_smoke.yaml` 的单任务 smoke，若认证通过再跑 OpenCode smoke。
