# Test-patch audit - wireapp__wire-webapp__13562

## 1. Task summary
- Folder: wireapp__wire-webapp__13562
- Ecosystem: npm_and_yarn
- Upgrade: typescript 4.7.4 -> 4.8.2
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `yarn test:types`

## 2. What is the breaking change?
TypeScript 4.8 tightens several type checks used by this project: catch variables are effectively `unknown`, generic component constraints become stricter, nullability/optional props are diagnosed differently, and some DOM/lib overload messages change.

## 3. What does Delta t (test.patch) actually do?
It fixes type errors in test helpers and specs: `Avatar.test.tsx` adds a non-null assertion and optional chaining on props, while `TestPage.tsx` constrains generic props to `Record<string, any>`, stores optional props safely, and renders with an explicit cast.

## 4. Does Delta t directly exercise the breaking change?
Yes. The verifier runs `yarn test:types`, so TypeScript diagnostics are the behavioral surface. Without Delta c, the upgraded compiler still reports source type errors in `AssetRepository`, `AccountForm`, `StoreEngineProvider`, `StorageService`, and `ComponentUtil`; with Delta c those source type failures are resolved or accepted in the Betterer baseline.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE - the upgraded TypeScript compiler rejects code that TypeScript 4.7 accepted or diagnosed differently, and the hidden type-test command requires the source migration.

## 6. Delta c nature
MIXED - real source type repairs plus a `.betterer.results` baseline update.

## 7. Soundness concerns / notes
This is a type-level witness rather than runtime behavior. That is acceptable here because the verifier command is explicitly a type-check command, not a lint/format-only command.

