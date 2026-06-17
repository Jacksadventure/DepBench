# Test-patch audit — prettier__prettier__8688

## 1. Task summary
- Folder: prettier__prettier__8688
- Ecosystem: npm_and_yarn
- Upgrade: @babel/parser 7.10.3 -> 7.10.4
- test_cmd: `yarn jest tests/js/classes-private-fields/ tests/js/record/ tests/js/tuple/ tests/misc/errors/js/ --ci`

## 2. What is the breaking change?
`@babel/parser` 7.10.4 changed parser behavior around several proposal syntaxes and can throw `undefined` for the HTML-like-comment error case. Prettier's Babel parser wrapper must tolerate an undefined thrown value and convert it into a normal parser error.

## 3. What does Δt (test.patch) actually do?
Δt adds parser fixture/snapshot coverage for optional chaining with private fields, invalid record methods, tuple holes/trailing commas, and updates the HTML-like-comment error snapshot from a specific Babel syntax error to `Unknown error (0:0)`.

## 4. Does Δt directly exercise the breaking change?
Yes. The verifier runs exactly the affected fixture directories. Without Δc, the parser wrapper assumes a real error object and mishandles the `undefined` throw from Babel 7.10.4; with Δc, it substitutes `{ message: "Unknown error" }` and the updated error snapshot passes.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — Δt directly captures the new parser behavior and requires Δc's source-side error normalization.

## 6. Δc nature
REAL_SOURCE_REPAIR — Δc changes `src/language-js/parser-babel.js` to handle an undefined thrown parser error.

## 7. Soundness concerns / notes
Most Δt changes are parser fixture/snapshot updates, but the error snapshot is tied to the actual source repair and the executed command covers it.
