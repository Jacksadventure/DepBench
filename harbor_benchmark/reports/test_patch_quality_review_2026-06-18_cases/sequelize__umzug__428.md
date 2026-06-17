# Test-patch audit - sequelize__umzug__428

## 1. Task summary
- Folder: sequelize__umzug__428
- Ecosystem: npm_and_yarn
- Upgrade: emittery 0.7.2 -> 0.8.1
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `npx jest test/umzug.test.ts --runInBand --coverage=false`

## 2. What is the breaking change?
`emittery` 0.8 changes the TypeScript/runtime shape used by Umzug. The old class declaration extends `emittery.Typed<UmzugEvents<Ctx>>`; Δc changes it to extend `emittery<UmzugEvents<Ctx>>`, matching the upgraded dependency.

## 3. What does Δt (test.patch) actually do?
Only reformats one callback in `test/umzug.test.ts` from a single-expression arrow body to a block body:
`ev => ev.context.counter++` becomes `{ ev.context.counter++; }`. No assertions or fixtures change.

## 4. Does Δt directly exercise the breaking change?
The Δt hunk itself does not; it is cosmetic. The selected Jest test still imports and instantiates `Umzug`, so with emittery 0.8 and no Δc the suite fails when compiling/importing the production class that extends the old `emittery.Typed` shape. With Δc, the same test file can run.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE - despite a formatting-only hidden test hunk, the verifier command exercises the repaired production class and fails under the upgraded emittery without Δc.

## 6. Δc nature
REAL_SOURCE_REPAIR - one production TypeScript inheritance clause is updated for emittery 0.8.

## 7. Soundness concerns / notes
- Δt adds no meaningful new coverage; this is an existing-test/import witness.
- If a future verifier transpiled without type/runtime checking of the inheritance target, this would be weaker, but the Jest command targets the affected `umzug.test.ts` path.
