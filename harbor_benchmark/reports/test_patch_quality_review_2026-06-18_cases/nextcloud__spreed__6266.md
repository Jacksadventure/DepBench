# Test-patch audit — nextcloud__spreed__6266

## 1. Task summary
- Folder: nextcloud__spreed__6266
- Ecosystem: npm_and_yarn
- Upgrade: vue-material-design-icons 4.12.1 -> 4.13.0
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `npm run test:unit -- --testPathPattern=Participant.spec`

## 2. What is the breaking change?
The `vue-material-design-icons` package changed the hand icon export used by this app. The old `vue-material-design-icons/Hand` import is replaced by `vue-material-design-icons/HandBackLeft`.

## 3. What does Δt (test.patch) actually do?
Updates `Participant.spec.js` to import `HandBackLeft` and to assert for `HandBackLeft` instead of `Hand` in every call-icon expectation.

## 4. Does Δt directly exercise the breaking change?
Yes. The verifier runs the participant unit test after applying Δt. With only Δm and Δt, the test imports the new icon while the production Vue component still imports/renders `Hand`; under the upgraded icon package the old import no longer matches the available component. Δc updates all production hand-icon usages to `HandBackLeft`.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — Δt updates the test expectation to the post-upgrade icon export and the targeted unit test fails until production components migrate to the new icon component.

## 6. Δc nature
REAL_SOURCE_REPAIR — Δc updates three Vue production components to import, register, and render `HandBackLeft`.

## 7. Soundness concerns / notes
- The test covers the participant sidebar component directly; Δc also updates two call-view components that are not part of the targeted `Participant.spec` run.
- The failure is a normal module/component API drift, not lint or dependency resolution.
