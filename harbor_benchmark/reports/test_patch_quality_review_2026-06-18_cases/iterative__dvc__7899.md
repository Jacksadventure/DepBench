# Test-patch audit — iterative__dvc__7899

## 1. Task summary
- Folder: iterative__dvc__7899
- Ecosystem: pip
- Upgrade: networkx 2.5,<2.8.3 -> 2.5,<2.8.5
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `python -m pytest tests/unit/command/test_dag.py tests/unit/command/test_imp_url.py -v`

## 2. What is the breaking change?
The newer NetworkX/pydot path exposes stricter DOT parsing/serialization around node labels that contain colons, paths, digits, backslashes, or non-ASCII characters. The old DVC DAG DOT renderer relabels nothing before `write_dot`, so labels like `stage: '1'` are emitted ambiguously and no longer match the expected safe quoted output.

## 3. What does Δt (test.patch) actually do?
Δt updates `tests/unit/command/test_dag.py` expected DOT output to include quoted node declarations, adds `test_show_dot_properly_escapes()` with labels such as `prepare:1`, `data/raw/1.dvc`, `data\\raw\\2.dvc`, `4`, and `train🚄`, and makes an unrelated fixture signature adjustment in `tests/unit/command/test_imp_url.py`.

## 4. Does Δt directly exercise the breaking change?
Yes. The new `test_show_dot_properly_escapes()` expects every problematic label to be quoted, e.g. `"prepare:1";` and `"data/raw/1.dvc" -> "prepare:1";`; the old `_show_dot` passes raw labels to `write_dot`, while Δc adds `_quote_label()` and `nx.relabel_nodes(G, _quote_label, copy=False)`.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — the DOT escaping assertions fail on P⊕Δm without Δc and pass after Δc quotes labels before NetworkX/pydot serialization.

## 6. Δc nature
REAL_SOURCE_REPAIR — Δc updates `dvc/commands/dag.py` and type annotates `dvc/repo/graph.py`; the substantive repair is source-side DOT label quoting.

## 7. Soundness concerns / notes
The `test_imp_url.py` fixture change is unrelated to the NetworkX break, but the `test_dag.py` additions provide a direct behavioral witness.
