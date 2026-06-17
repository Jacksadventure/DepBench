# Test-patch audit — Graylog2__graylog2-server__23926

## 1. Task summary
- Folder: Graylog2__graylog2-server__23926
- Ecosystem: maven
- Upgrade: io.modelcontextprotocol.sdk:mcp-bom 0.11.2 -> 0.14.1
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `<could not extract>`

## 2. What is the breaking change?
MCP SDK 0.14.1 split the `mcp` artifact into `mcp-core` + `mcp-json-jackson2` and changed the `Tool` schema API: `inputSchema()`/`outputSchema()` return types moved from `String`/`Optional<String>` to `Optional<McpSchema.JsonSchema>` / `Optional<Map<String,Object>>`, and `Tool.builder().inputSchema(...)`/`outputSchema(...)` now take the new types (and `inputSchema` became Optional-gated).

## 3. What does Δt (test.patch) actually do?
- `graylog2-server/src/test/java/org/graylog/mcp/server/McpServiceTest.java`: one-line change in `testListTools()` — updates the `mockTool.inputSchema()` stub from `thenReturn("{}")` (old `String` return) to `thenReturn(Optional.empty())` (new `Optional<McpSchema.JsonSchema>` return). No new test cases.

## 4. Does Δt directly exercise the breaking change?
Yes. `testListTools()` exercises `McpService.handle()` which calls `tool.inputSchema().ifPresent(builder::inputSchema)` (post-Δc). With Δt the mock returns the new `Optional` type matching the changed `Tool.inputSchema()` signature; without Δc the source `Tool` still declares `inputSchema()` returning `String`, so the test mock (`Optional.empty()`) and the `McpService` call site (`tool.inputSchema().ifPresent(...)`) fail to compile against the new SDK → FAIL, and pass with Δc.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — the Δt stub matches the new `inputSchema()` return type, so P⊕Δm⊕Δt fails to compile (source still on old signature) and P⊕Δm⊕Δc⊕Δt compiles and passes.

## 6. Δc nature
REAL_SOURCE_REPAIR — `McpService.java` and `Tool.java` are migrated to the new MCP SDK API (Optional-gated `inputSchema`/`outputSchema`, `McpSchema.JsonSchema` / `Map<String,Object>` field types, `objectMapper.convertValue`), driven by the manifest's `mcp`→`mcp-core`+`mcp-json-jackson2` split.

## 7. Soundness concerns / notes
- `test_cmd` could not be extracted from `test_state.py` — the verifier command is missing, so it is unclear how the harness actually invokes the test; needs a Maven test invocation to be runnable.
- The witness is compile-level (compiled language, allowed by the definition), but Δt is a single mock-stub adaptation rather than a deep behavioral assertion of the new schema handling.
