# Handoff: Codex Last Chat-Completions Version

Date: 2026-06-27

Question:
- User asked which Codex version last supported `wire_api = "chat"` / chat completions, referencing commit `d2394a2494651b5adeddc940b6c309fd407ac1e3`.

Findings:
- Commit `d2394a2494651b5adeddc940b6c309fd407ac1e3` is `chore: nuke chat/completions API (#10157)`, dated 2026-02-03 11:31:57 +0000.
- Local tag boundary:
  - `rust-v0.95.0-alpha.5` (`d65634a2710e`) does **not** contain the removal commit and still has `WireApi::{Responses, Chat}` plus chat endpoint/request/SSE files.
  - `rust-v0.95.0-alpha.6` (`65fa82bbcc89`) contains the removal commit; chat endpoint/request/SSE files are gone and `wire_api = "chat"` deserializes to an explicit unsupported error.
  - `rust-v0.95.0` also contains the removal.
  - Last stable before removal is `rust-v0.94.0` (`a334db553297`).
- npm confirmed installable versions:
  - `@openai/codex@0.95.0-alpha.5`
  - `@openai/codex@0.95.0-alpha.6`
  - `@openai/codex@0.94.0`
  - `@openai/codex@0.95.0`

Answer to give:
- Last overall version with chat support: `@openai/codex@0.95.0-alpha.5`.
- Last stable version with chat support: `@openai/codex@0.94.0`.
- First version without chat support: `@openai/codex@0.95.0-alpha.6`; stable `0.95.0` is already no-chat.
