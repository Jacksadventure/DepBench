# Test-patch audit — jenkinsci__warnings-ng-plugin__1278

## 1. Task summary
- Folder: jenkinsci__warnings-ng-plugin__1278
- Ecosystem: maven
- Upgrade: jenkins-core 2.334 -> 2.354
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `mvn ... -pl ui-tests -am -Dtest=UiTest test` / fallback `-f ui-tests/pom.xml -Dtest=UiTest test`

## 2. What is the breaking change?
Recent Jenkins UI/control behavior changed how checkboxes and radio buttons need to be selected in the acceptance-test page objects. Direct `find(...).click()`/path-specific controls are no longer reliable for the upgraded Jenkins core.

## 3. What does Δt (test.patch) actually do?
It updates `UiTest.createDashboardWithStaticAnalysisPortlet` to call `portlet.setHideCleanJobs(hideCleanJobs)` and `portlet.setShowIcons(showIcons)` instead of conditionally toggling the two checkboxes.

## 4. Does Δt directly exercise the breaking change?
Partially but sufficiently. The hidden test now calls methods that only exist after Δc, so P⊕Δm⊕Δt fails to compile without the page-object repair. With Δc, those methods use `Control.check(...)`, and the related radio-button helper also uses JavaScript click for the Jenkins 2.354 UI. The witness is mostly a compile/API gate over the page-object repair rather than a new assertion against the rendered UI.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — the upgraded UI-test source fails against Δt without the new setter API and passes with Δc; the repaired page-object behavior is the human fix for Jenkins 2.354 checkbox/radio selection.

## 6. Δc nature
REAL_SOURCE_REPAIR — updates UI-test page-object source under `ui-tests/src/main/java`: adds robust checkbox setters, a radio-button lookup helper, and JavaScript-backed radio selection.

## 7. Soundness concerns / notes
- The files live in a UI-test module, so they are test-support source rather than product runtime code.
- Δt only covers the checkbox setter API directly; the radio-button JavaScript click change is repaired in Δc but is not directly modified by Δt.
