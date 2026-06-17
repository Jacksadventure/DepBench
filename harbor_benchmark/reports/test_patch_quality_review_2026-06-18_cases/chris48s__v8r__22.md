# Test-patch audit — chris48s__v8r__22

## 1. Task summary
- Folder: chris48s__v8r__22
- Ecosystem: npm_and_yarn
- Upgrade: js-yaml 3.14.0 -> 4.0.0 (metadata labels the lockfile integrity field)
- test_cmd: `V8R_CACHE_NAME=v8r-test npx mocha 'src/**/*.spec.js' --reporter spec`

## 2. What is the breaking change?
js-yaml 4 removes the old `safeLoad` API. YAML parsing must use `yaml.load()` instead.

## 3. What does Δt (test.patch) actually do?
`src/cli.spec.js` adds a CLI test that validates a YAML file (`./testfiles/valid.yaml`) against a mocked schema endpoint and expects a successful validation message.

## 4. Does Δt directly exercise the breaking change?
Yes. The new test drives the YAML parsing path. Without Δc, `yaml.safeLoad` is missing under js-yaml 4 and YAML validation fails; with Δc, `yaml.load` parses the fixture and the CLI succeeds.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — Δt directly reaches the removed js-yaml API and Δc is the required replacement.

## 6. Δc nature
MIXED — real source repair in `src/cli.js` plus an added YAML fixture under `testfiles/valid.yaml`.

## 7. Soundness concerns / notes
- The batch metadata's `library` field appears to have captured an integrity value, but the manifest patch clearly upgrades `js-yaml`.
- The source repair is small and directly tied to the hidden test.

