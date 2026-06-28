## Handoff: Copilot token written to `.env`

User asked to create/write a GitHub/Copilot token for the custom Copilot and
OpenCode runners.

Actions:

- Confirmed `gh auth status` is authenticated.
  - Active account shown by `gh`: `hrz6976`.
  - Another inactive account exists: `v-runzhihe_microsoft`.
- Added `.gitignore` with:
  - `.env`
- Wrote the active `gh auth token` into `.env` without printing the token.
- `.env` permissions are `600`.
- Token aliases written:
  - `COPILOT_GITHUB_TOKEN`
  - `COPILOT_API_KEY`
  - `GH_TOKEN`
  - `GITHUB_TOKEN`
- Verified:
  - `git check-ignore -v .env` reports `.gitignore:1:.env`.
  - Sourcing `.env` sets all four token keys.

Important:

- Harbor does not automatically load `.env`. Source it for local smoke runs:

```bash
set -a
. ./.env
set +a
uv run harbor run -c configs/custom_opencode_copilot_smoke.yaml -y
```

- Do not print or commit `.env`.
