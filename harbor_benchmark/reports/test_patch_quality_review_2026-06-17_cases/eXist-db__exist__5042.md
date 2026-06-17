# Test-patch audit — eXist-db__exist__5042

## 1. Task summary
- Folder: eXist-db__exist__5042
- Ecosystem: maven
- Upgrade: com.siemens.ct.exi:exificient 0.9.3 -> 1.0.7
- Flagged in problematic_prs_review_2026-06-10.md: NO (random control)
- test_cmd: `<could not extract>` (test_state.py did not yield a runnable command — verifier-config concern, see §7)

## 2. What is the breaking change?
exificient 1.0.7 repackaged its classes and split the artifact into `exificient-core` / `exificient-grammars` / `exificient` modules. Import paths moved: `com.siemens.ct.exi.EXIFactory` → `com.siemens.ct.exi.core.EXIFactory`, `com.siemens.ct.exi.exceptions.EXIException` → `com.siemens.ct.exi.core.exceptions.EXIException`, `com.siemens.ct.exi.grammars.Grammars` → `com.siemens.ct.exi.core.grammars.Grammars`, `com.siemens.ct.exi.helpers.DefaultEXIFactory` → `com.siemens.ct.exi.core.helpers.DefaultEXIFactory`, and `com.siemens.ct.exi.api.sax.SAXEncoder/SAXDecoder` → `com.siemens.ct.exi.main.api.sax.*`. The old imports no longer resolve → Maven compile failure.

## 3. What does Δt (test.patch) actually do?
Touches one file: `exist-core/src/test/java/org/exist/util/serializer/EXISerializerTest.java`. A single one-line import fix — `com.siemens.ct.exi.api.sax.SAXEncoder` → `com.siemens.ct.exi.main.api.sax.SAXEncoder`. No new test cases, no new assertions, no fixtures — just making the existing test compile against the new package layout.

## 4. Does Δt directly exercise the breaking change?
Yes, at compile level. `EXISerializerTest` directly imports `SAXEncoder` (used to assert against the EXI-serialized output) and exercises `EXISerializer` — the production class repaired in Δc. On P⊕Δm⊕Δt the test file compiles but the production `EXISerializer.java` (and the two `exi` module functions) still reference the old `com.siemens.ct.exi.*` packages → the module fails to compile → build/test FAIL; on P⊕Δm⊕Δc⊕Δt all imports are fixed → `EXISerializerTest` compiles and runs → PASS.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — without Δc the production EXI sources do not compile (import-path break), so TEST(P⊕Δm⊕Δt) FAILs; with Δc (and Δt fixing the test import) it compiles and the EXI serializer test passes.

## 6. Δc nature
REAL_SOURCE_REPAIR — pure import-path migration in three production Java files: `exist-core/.../EXISerializer.java`, `extensions/modules/exi/.../DecodeExiFunction.java`, `extensions/modules/exi/.../EncodeExiFunction.java` (no logic changes, just `com.siemens.ct.exi.*` → `com.siemens.ct.exi.core.*` / `...main.api.sax.*`). The manifest also adds the new `exificient-core`/`exificient-grammars` module dependencies (part of Δm).

## 7. Soundness concerns / notes
- **test_cmd could not be extracted** from `test_state.py`; the verifier command for this Maven task is not confirmed from the bundle. The static patch analysis still establishes a clean compile-level witnessed break, but the missing command is a verifier-config risk worth confirming against the actual `test_state.py`.
- Δt is a one-import "mirror" of Δc (the test needed the same package rename as production). This is the standard pattern for package-rename breaks and is a legitimate witness, though the test adds no new behavioral assertion beyond "still compiles and runs the EXI round-trip".
- The Δm manifest change is unusually large (adds `exificient-core`/`exificient-grammars` deps + xerces exclusions across 3 poms); that is correct for the module split and does not affect the verdict.
