# Test-patch audit — Azure-Samples__chat-with-your-data-solution-accelerator__894

## 1. Task summary
- Folder: Azure-Samples__chat-with-your-data-solution-accelerator__894
- Ecosystem: pip
- Upgrade: semantic-kernel 0.9.7b1 -> 0.9.8b1
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `poetry run pytest code/tests/utilities/orchestrator/test_SemanticKernel.py code/tests/functional/tests/backend_api/sk_orchestrator/test_response_without_tool_call.py -v`

## 2. What is the breaking change?
semantic-kernel 0.9.8b1 removed `semantic_kernel.connectors.ai.open_ai.utils.get_tool_call_object` and replaced the `settings.tools = ...` mechanism with `settings.function_call_behavior = FunctionCallBehavior.EnableFunctions(filters={"included_plugins": [...]})`. The new API also causes the OpenAI request payload to include `"tool_choice": "auto"`.

## 3. What does Δt (test.patch) actually do?
- `test_response_without_tool_call.py`: adds `"tool_choice": "auto"` to the expected OpenAI chat-completions request payload assertion.
- `test_SemanticKernel.py`: renames `test_openai_functions_included`→`test_kernel_function_call_behavior`, imports `EnabledFunctions`, and replaces a large hardcoded `tools == [...]` list assertion with assertions on `function_call_behavior.auto_invoke_kernel_functions is False`, `enable_kernel_functions is True`, and `filters == {"included_plugins": ["Chat"]}`.

## 4. Does Δt directly exercise the breaking change?
Yes. `test_kernel_function_call_behavior` asserts `prompt_execution_settings.function_call_behavior` (new v0.9.8 attribute) — on P⊕Δm the source still sets `settings.tools = get_tool_call_object(...)`, so `function_call_behavior` is unset and the assertion fails (or `get_tool_call_object` import errors at runtime). The `tool_choice: "auto"` expectation in the functional test likewise only holds once `FunctionCallBehavior.EnableFunctions` is used (Δc).

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — Δt asserts the new `function_call_behavior` API surface and the `tool_choice:"auto"` payload, both of which fail on P⊕Δm (old `get_tool_call_object`/`settings.tools` path) and pass on P⊕Δm⊕Δc.

## 6. Δc nature
REAL_SOURCE_REPAIR — `code/backend/batch/utilities/orchestrator/SemanticKernel.py` swaps the `get_tool_call_object` import for `FunctionCallBehavior` and changes `settings.tools = get_tool_call_object(kernel=..., filter={"include_plugin":["Chat"]})` to `settings.function_call_behavior = FunctionCallBehavior.EnableFunctions(filters={"included_plugins":["Chat"]})`.

## 7. Soundness concerns / notes
Clean witnessed task; no concerns. Δt and Δc are tightly coupled to the same API replacement, and the run tests cover both the unit-level (`function_call_behavior` attributes) and functional-level (`tool_choice` in the mocked OpenAI call) aspects of the breaking change.
