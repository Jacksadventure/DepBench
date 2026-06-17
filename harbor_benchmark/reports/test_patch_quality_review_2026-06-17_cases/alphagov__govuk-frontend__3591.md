# Test-patch audit — alphagov__govuk-frontend__3591

## 1. Task summary
- Folder: alphagov__govuk-frontend__3591
- Ecosystem: npm_and_yarn
- Upgrade: rollup 0.59.4 -> 3.21.5 (also swaps `rollup-plugin-node-resolve`/`rollup-plugin-replace`/`terser` for `@rollup/plugin-node-resolve`/`@rollup/plugin-replace`/`@rollup/plugin-terser`)
- Flagged in problematic_prs_review_2026-06-10.md: YES
- test_cmd: `npm run build:package --workspace govuk-frontend && npx jest --selectProjects 'Build tasks' --testMatch '**/*package.test*'; npm run build:release --workspace govuk-frontend && npx jest --selectProjects 'Build tasks' --testMatch '**/*release.test*'`

## 2. What is the breaking change?
rollup 0.59 -> 3.x is a multi-major jump: plugin packages were renamed (`rollup-plugin-*` -> `@rollup/plugin-*`), `experimentalPreserveModules` became `preserveModules` (output option), `terser` is now an output plugin (`@rollup/plugin-terser`) instead of a post-process `minify()` call, and rollup 3.x changed ESM default export emission from `export default X` to `export { X as default }`.

## 3. What does Δt (test.patch) actually do?
- `packages/govuk-frontend/tasks/build/package.test.mjs`: changes ESM output assertion `expect(moduleTextESM).toContain(\`export default ${className}\`)` -> `toContain(\`export { ${className} as default }\`)`.
- `packages/govuk-frontend/tasks/build/release.test.mjs`: changes version-string assertion `expect(javascript).toContain(\`.version="${pkg.version}",\`)` -> `toContain(\`.version="${pkg.version}"\`)` (drops trailing comma).
Both are output-format assertions against the built bundle, run after `npm run build:package` / `build:release`.

## 4. Does Δt directly exercise the breaking change?
Partially. The `export { X as default }` assertion is **rollup-version-determined**: rollup 3.x (installed via Δm) emits this format regardless of how `scripts.mjs` is written, so this assertion passes on P⊕Δm whenever the build runs — it does not discriminate Δc. The `.version="X"` (no comma) assertion is the only one that could discriminate old-pipeline (terser `minify()` post-process) vs new-pipeline (`@rollup/plugin-terser` output plugin), but only if both pipelines actually run and produce different comma placement. There is no assertion that directly probes the renamed plugin imports or the `preserveModules` option usage.

## 5. Coverage verdict
UNWITNESSED — `flagged_in_problematic_review: True` indicates P⊕Δm⊕Δt passes without Δc; this is consistent with the discriminating assertion (`export { X as default }`) being a rollup-version property set by Δm itself, and the build either succeeding on stale/transitive deps or the comma difference not manifesting for the version string.

## 6. Δc nature
REAL_SOURCE_REPAIR — `shared/tasks/scripts.mjs` is genuinely rewritten for rollup 3.x: new `@rollup/plugin-*` imports, `experimentalPreserveModules` -> output `preserveModules`+`entryFileNames`, `bundle.generate` -> `bundle.write`, removal of `minifyJavaScript()` helper in favor of `terser()` output plugin, `preventAssignment: true` on `replace()`. Real API migration, but its effect on the two specific assertions Δt checks is marginal.

## 7. Soundness concerns / notes
- The discriminating assertion (`export { X as default }`) is determined by the **rollup version (Δm)**, not by `scripts.mjs` (Δc). So an agent who simply re-runs the build with rollup 3.x gets that assertion for free without reproducing the Δc API migration — a textbook no_code_pass driver.
- Ambiguity: if the build fails on P⊕Δm because `rollup-plugin-node-resolve` / `rollup-plugin-replace` are no longer in the lockfile (clean `npm ci`), the pre-phase FAIL is a **dependency-resolution error**, which the breaking-change definition excludes. If the build succeeds (stale/transitive deps), Δt passes without Δc. Either way the task is not a clean witnessed case.
- The comma-removal assertion in `release.test.mjs` is the only assertion that could tie to Δc (terser-output-plugin vs post-minify), but it is fragile and apparently does not flip the outcome per the flagged status.
