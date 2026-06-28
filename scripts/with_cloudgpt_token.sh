#!/usr/bin/env bash
set -euo pipefail

DEFAULT_TENANT_ID="72f988bf-86f1-41af-91ab-2d7cd011db47"
DEFAULT_RESOURCE="api://feb7b661-cac7-44a8-8dc1-163b63c23df2"

usage() {
  cat <<'USAGE'
Refresh a CloudGPT Azure AD bearer token, export token aliases, then run a command.

Usage:
  scripts/with_cloudgpt_token.sh [--tenant TENANT_ID] [--resource APP_ID_URI] -- COMMAND [ARGS...]

Environment overrides:
  CLOUDGPT_AAD_TENANT_ID
  CLOUDGPT_AAD_RESOURCE

Example:
  scripts/with_cloudgpt_token.sh -- uv run harbor run -c configs/deepseek_v4_pro_cloudgpt_codex_opencode.yaml -y
USAGE
}

tenant_id="${CLOUDGPT_AAD_TENANT_ID:-$DEFAULT_TENANT_ID}"
resource="${CLOUDGPT_AAD_RESOURCE:-$DEFAULT_RESOURCE}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --tenant)
      tenant_id="${2:-}"
      shift 2
      ;;
    --resource)
      resource="${2:-}"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    --)
      shift
      break
      ;;
    *)
      break
      ;;
  esac
done

if [[ $# -eq 0 ]]; then
  usage >&2
  exit 2
fi

if [[ -z "$tenant_id" || -z "$resource" ]]; then
  echo "with_cloudgpt_token.sh: tenant and resource are required" >&2
  exit 2
fi

if ! command -v az >/dev/null 2>&1; then
  echo "with_cloudgpt_token.sh: az CLI is required to refresh the CloudGPT token" >&2
  exit 1
fi

if token="$(az account get-access-token \
  --tenant "$tenant_id" \
  --resource "$resource" \
  --query accessToken \
  -o tsv 2>/dev/null)"; then
  token="${token//$'\n'/}"
fi

if [[ -z "${token:-}" ]]; then
  token="$(az account get-access-token \
    --tenant "$tenant_id" \
    --scope "$resource/.default" \
    --query accessToken \
    -o tsv)"
  token="${token//$'\n'/}"
fi

if [[ -z "$token" ]]; then
  echo "with_cloudgpt_token.sh: Azure CLI returned an empty CloudGPT token" >&2
  exit 1
fi

export CLOUDGPT_OPENAI_TOKEN="$token"

# Codex and OpenCode both use OpenAI-compatible clients, so pass the same
# CloudGPT bearer token through their expected API-key env names.
export OPENAI_API_KEY="$token"
export CODEX_API_KEY="$token"
export AZURE_OPENAI_API_KEY="$token"

echo "with_cloudgpt_token.sh: refreshed CloudGPT token" >&2
exec "$@"
