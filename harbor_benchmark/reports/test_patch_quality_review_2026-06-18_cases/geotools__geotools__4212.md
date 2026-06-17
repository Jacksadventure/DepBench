# Test-patch audit — geotools__geotools__4212

## 1. Task summary
- Folder: geotools__geotools__4212
- Ecosystem: maven
- Upgrade: snakeyaml 1.32 -> 2.0
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `<could not extract>` (test_state.py command not parseable from bundle)

## 2. What is the breaking change?
snakeyaml 2.0 removed the no-arg `Representer()` and `SafeConstructor()` constructors (now requiring `DumperOptions` / `LoaderOptions` arguments), which is a compile-breaking API change for `YamlUtil`/`YsldRepresenter`. It also changed the exception thrown for disallowed global tags from `ConstructorException` ("could not determine a constructor") to `ComposerException` ("Global tag is not allowed").

## 3. What does Δt (test.patch) actually do?
- `modules/extension/ysld/src/test/java/org/geotools/ysld/parse/YsldParseTest.java`: modifies the existing `testDeserializationAttempt` test — swaps the expected exception type and message from `ConstructorException` + `"could not determine a constructor"` to `ComposerException` + `"Global tag is not allowed"` for the `!!java.util.Date` unsafe-tag parse case.
- No new tests, no fixtures, no infra.

## 4. Does Δt directly exercise the breaking change?
Yes. The patched assertion `catch (ComposerException e) { assertThat(e.getMessage(), containsString("Global tag is not allowed")); }` directly targets the snakeyaml-2.0 behavioral change for unsafe global tags. On P⊕Δm the project fails to *compile* (`new Representer()` / `new SafeConstructor()` removed in 2.0), so the test cannot even run → FAIL; on P⊕Δm⊕Δc the constructors are migrated and `Ysld.parse("!!java.util.Date...")` throws the new `ComposerException` → PASS.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — compile failure without Δc plus a behavioral assertion on the snakeyaml-2.0 exception type makes this a clean witness.

## 6. Δc nature
REAL_SOURCE_REPAIR — `YamlUtil.java` migrates `new Representer()`→`new Representer(dumperOptions)` and `new SafeConstructor()`→`new SafeConstructor(new LoaderOptions())`; `YsldRepresenter.java` calls `super(new DumperOptions())`.

## 7. Soundness concerns / notes
- The verifier `test_cmd` could not be extracted from the bundle (`<could not extract>`); confirm `tests/test_state.py` actually targets `YsldParseTest#testDeserializationAttempt` (or the ysld module) so the oracle runs.
- Task metadata is malformed: the new version is recorded as `to` (instruction title, `library` header) even though `manifest.patch` correctly bumps to `2.0`. Cosmetic, but the instruction reads "snakeyaml 1.32 → to", which would confuse an agent.
