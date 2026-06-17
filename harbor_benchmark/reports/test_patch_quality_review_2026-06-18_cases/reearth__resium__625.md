# Test-patch audit — reearth__resium__625

## 1. Task summary
- Folder: reearth__resium__625
- Ecosystem: npm_and_yarn
- Upgrade: react >=18.2.0 -> >=18.2.0 (lockfile/runtime dependency refresh)
- test_cmd: `yarn run test --run src/Entity/Entity.test.tsx src/core/component.test.tsx src/core/utils.test.ts`

## 2. What is the breaking change?
The repair addresses async React/Cesium lifecycle behavior and helper typing after the dependency refresh: component mount/update/unmount paths now wait on async creation/update, shared promise detection is centralized in `isPromise`, and several Cesium prop surfaces are updated.

## 3. What does Δt (test.patch) actually do?
Existing component tests are changed to wait for asynchronous updates with `waitFor`, and a new `src/core/utils.test.ts` imports `isPromise` and checks plain objects versus real promises.

## 4. Does Δt directly exercise the breaking change?
Yes. The new `isPromise` test fails to compile/import without the helper introduced by Δc. The component tests also exercise the async update timing that Δc changes, although several `waitFor` calls are not awaited and are therefore weaker as runtime assertions.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — at minimum the hidden `isPromise` test is a direct source-surface witness, and the component tests target the async lifecycle repaired by Δc.

## 6. Δc nature
MIXED — substantial production source repair across core/component hooks and Cesium components, plus story/example churn in `Cesium3DTileset.stories.tsx`.

## 7. Soundness concerns / notes
- Some `waitFor` wrappers in Δt are not awaited, which weakens those particular assertions.
- The added `isPromise` import/test gives a concrete compile/runtime witness despite the weaker async assertions.

