# Test-patch audit — apache__iceberg-python__159

## 1. Task summary
- Folder: apache__iceberg-python__159
- Ecosystem: pip
- Upgrade: pydantic 2.4.2 -> 2.5.2
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `python -m pytest tests/cli/test_console.py`

## 2. What is the breaking change?
The CLI path mutates a Pydantic-backed table metadata object by deleting `table.metadata.properties` before emitting the "Writing is WIP" error. Under the upgraded Pydantic/Pydantic-core combination, that field deletion is no longer a safe operation on the model object used by PyIceberg.

## 3. What does Δt (test.patch) actually do?
`tests/cli/test_console.py` relaxes `test_properties_remove_table` from an exact output match (`"Writing is WIP\n1\n"`) to `assert "Writing is WIP" in result.output`.

## 4. Does Δt directly exercise the breaking change?
Yes, in a narrow way. Without Δc, the deletion happens before the intended WIP exception path and can prevent the expected CLI output under the new Pydantic behavior. With Δc, the CLI stops deleting `table.metadata.properties`, reaches the intended `output.exception(NotImplementedError("Writing is WIP"))` path, and the relaxed Δt assertion passes.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — the verifier exercises the exact CLI branch repaired by Δc and distinguishes the unrepaired upgraded state from the repaired state.

## 6. Δc nature
REAL_SOURCE_REPAIR — `pyiceberg/cli/console.py` removes the unsafe deletion of `table.metadata.properties` before returning the WIP error.

## 7. Soundness concerns / notes
The hidden test is weaker than ideal because it relaxes an assertion rather than adding a precise assertion for the Pydantic failure mode. Still, the repaired line is in the tested path and the witness is source-behavior relevant, not lint or dependency resolution.
