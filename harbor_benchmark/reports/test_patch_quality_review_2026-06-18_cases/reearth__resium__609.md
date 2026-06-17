# Test-patch audit — reearth__resium__609

## 1. Task summary
- Folder: reearth__resium__609
- Ecosystem: npm_and_yarn
- Upgrade: cesium 1.103.0 -> 1.107.0
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `yarn run test --run src/Model/Model.test.ts src/Viewer/Viewer.test.ts src/core/component.test.tsx`

## 2. What is the breaking change?
Cesium 1.107 changes several construction and readiness APIs used by Resium. Examples include async factory methods such as `Model.fromGltfAsync`, `Cesium3DTileset.fromUrl`, async imagery/terrain provider creation, replacement/removal of `readyPromise`-style readiness, and viewer/widget option shifts from `imageryProvider`/`baseLayer` and `terrainProvider` handling.

## 3. What does Δt (test.patch) actually do?
- `Model.test.ts`: updates the exported type name from the old typo `ModalOtherProps` to `ModelOtherProps`.
- `Viewer.test.ts`: marks `terrainProvider` as an intentionally handled non-Cesium prop.
- `core/component.test.tsx`: adds an async creation test verifying that a component whose `create` returns a promise eventually exposes the Cesium element.

## 4. Does Δt directly exercise the breaking change?
Yes. The async component test directly covers the core hook change needed for Cesium's async creation APIs. The Model and Viewer type tests also reflect the post-Cesium API split where certain values are handled as Resium "other props" rather than direct Cesium constructor props. Without Δc, the async create path does not await the promise and the type/prop expectations do not match.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — Δt checks the async component lifecycle and updated prop/type split required by the Cesium upgrade, and Δc implements those production changes.

## 6. Δc nature
REAL_SOURCE_REPAIR — Δc updates Resium source components and hooks for Cesium 1.107 async APIs and prop changes. A few Storybook/example files are updated too, but the load-bearing changes are production source.

## 7. Soundness concerns / notes
- The verifier covers representative Model, Viewer, and core hook behavior, not every Cesium component touched by Δc.
- The tested async lifecycle is a strong witness for the main upgrade adaptation.
