# Test-patch audit — owncloud__web__11511

## 1. Task summary
- Folder: owncloud__web__11511
- Ecosystem: npm_and_yarn
- Upgrade: vue 3.4.38 -> 3.5.4 (also @vue/compiler-dom, @vue/compiler-sfc, @vue/shared)
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `pnpm exec vitest run <12 spec files> --no-coverage --pool=forks`

## 2. What is the breaking change?
Vue 3.5 tightened reactivity/typing (`ref`/`computed` overloads, stricter `Ref` inference) and changed how mock-extended's `mockDeep` interacts with vue-router's now-readonly `currentRoute`. Components/test-helpers that relied on `ref<T[]>([])` inference, Options-API `render()` with `this.$props`/`this.$slots`, or `mockDeep<Router>({currentRoute: ref(...)})` need migration to explicit `Ref<T>` annotations, `setup(props)` returning a render fn, and `mock<Router>()` + a `writable()` escape hatch.

## 3. What does Δt (test.patch) actually do?
Touches 12 spec files + 1 snapshot:
- `CreateAndUpload.spec.ts`, `ResourceTable.spec.ts`, `FileSideBar.spec.ts`: switch composable mocks from `mock<...>({actions/selectedResources: ref(...)})` to `mock<...>()` then assign `actions = computed(...)`.
- `SpaceContextActions.spec.ts`, `AppBar.spec.ts`: add `name: ''` to `mock<RouteLocation>(...)`.
- `sdk.spec.ts`: replace `mock<Router>({currentRoute: ref(...)})` with `mock<Router>()` + `writable(router).currentRoute = ref(...)`.
- `GenericSpace.spec.ts`: loosen `currentRoute` type to `{name?; path?}`.
- `ItemFilterInline.spec.ts`, `ItemFilter.spec.ts`, `ItemFilterToggle.spec.ts`: drop `unref(mocks.$router.currentRoute).query` checks in favor of `expect(mocks.$router.push).toHaveBeenCalledWith(expect.objectContaining({query: ...}))`.
- `Projects.spec.ts` + `Projects.spec.ts.snap`: remove a stale comment and update snapshot (`sort-by="undefined" sort-dir="desc" view-size="NaN"` → `sort-by="name" sort-dir="asc" view-size="1"`).
- `resolvePublicLink.spec.ts`: add `useRouteQuery` to the `@ownclouders/web-pkg` mock.

## 4. Does Δt directly exercise the breaking change?
Partially. The load-bearing witness is the dependency on Δc's test-helper rewrite in `defaultComponentMocks.ts` (which initializes `$route.meta` and makes `currentRoute` writable via `writable()`); specs whose components read `$route.meta`/`currentRoute` fail on P⊕Δm without that helper change. However, several Δt edits are independent of Δc: the `Projects.spec.ts.snap` snapshot change reflects Vue-3.5 rendering (sort-by/view-size) that happens regardless of Δc, and the `mock()->assign computed(...)` pattern in `CreateAndUpload`/`ResourceTable`/`FileSideBar` is a test-side modernization that does not require the production-component Δc. On balance TEST(P⊕Δm⊕Δt)=FAIL and TEST(P⊕Δm⊕Δc⊕Δt)=PASS (consistent with not being flagged), but the witness is narrow.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — the spec set fails on P⊕Δm (vue-3.5 mock/reactivity incompatibility surfaced via the `defaultComponentMocks`/`defaultPlugins` helpers) and passes on P⊕Δm⊕Δc, though the witness is concentrated in the test-helper subset of Δc.

## 6. Δc nature
MIXED — production-component Vue-3.5 typing fixes in `AddToGroupsModal.vue`, `RemoveFromGroupsModal.vue` (`ref<T[]>([])`→`Ref<T[]>`), `PortalTarget.vue` (`computed<T>()`); plus test-infrastructure rewrites in `packages/web-test-helpers/src/defaultPlugins.ts` (RouterLink stub `render()`→`setup(props)` returning a render fn) and `packages/web-test-helpers/src/mocks/defaultComponentMocks.ts` (`mockDeep<Router>`→`mock<Router>()`+`writable`+`$route.meta` init). The latter two are nominally "source" (under `packages/`, not `tests/`) but are test helpers.

## 7. Soundness concerns / notes
- The production-component Δc edits (AddToGroupsModal/RemoveFromGroupsModal/PortalTarget) are pure TS-typing fixes with no runtime effect under vitest (esbuild strips types), so they are NOT runtime-witnessed by Δt; an agent could leave them undone and still pass.
- The actual runtime witness is narrow: `defaultComponentMocks.ts`'s `$route.meta` initialization and `writable(currentRoute)`. An agent could pass by editing only the two test-helper files.
- The `Projects.spec.ts.snap` snapshot update is driven by Vue 3.5's rendering, not by any Δc file — it would match with or without the production Δc. This is benign for the gate (Δt is applied verbatim) but means the snapshot is not a Δc witness.
- Δc putting test-helper edits in `packages/web-test-helpers/**` blurs the "production source only" constraint; the instruction tells the agent to restrict changes to source, which technically permits these files, but they are test infrastructure.
