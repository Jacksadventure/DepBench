# Test-patch audit — nextcloud__text__8485

## 1. Task summary
- Folder: nextcloud__text__8485
- Ecosystem: npm_and_yarn
- Upgrade: @tiptap/core 3.22.3 -> 3.22.4 (also @tiptap/extension-collaboration, -drag-handle, -drag-handle-vue-2, @tiptap/pm, @tiptap/vue-2 → 3.22.4; adds direct deps `prosemirror-markdown` and `prosemirror-schema-basic`)
- Flagged in problematic_prs_review_2026-06-10.md: YES
- test_cmd: `npm run test -- src/tests/plugins/linkBubble.spec.js src/tests/plugins/searchQuery.spec.js`

## 2. What is the breaking change?
@tiptap/pm 3.22.4 dropped the re-exports of `prosemirror-markdown` and `prosemirror-schema-basic` (package-lock shows it removed `prosemirror-collab`, `prosemirror-inputrules`, `prosemirror-markdown`, `prosemirror-menu`, `prosemirror-schema-basic`, `prosemirror-trailing-node` from its deps). So `import { MarkdownSerializer, defaultMarkdownSerializer } from '@tiptap/pm/markdown'` and `import { schema } from '@tiptap/pm/schema-basic'` no longer resolve; they must import from the standalone `prosemirror-markdown` / `prosemirror-schema-basic` packages (now declared as direct deps).

## 3. What does Δt (test.patch) actually do?
- `src/tests/plugins/linkBubble.spec.js`: changes `import { schema } from '@tiptap/pm/schema-basic'` → `from 'prosemirror-schema-basic'`.
- `src/tests/plugins/searchQuery.spec.js`: same `@tiptap/pm/schema-basic` → `prosemirror-schema-basic` import swap.
- No new assertions or test cases; the specs still exercise `../../plugins/links.js` (`hideLinkBubble`, `linkBubble`, `setActiveLink`, `nextMatch`, `previousMatch`).

## 4. Does Δt directly exercise the breaking change?
No. The Δt imports `schema` from the newly-added direct dep `prosemirror-schema-basic` (available regardless of Δc) and `EditorState`/`Plugin` from `@tiptap/pm/state` (still present in 3.22.4), then drives `links.js` — which Δc does NOT modify. The four files Δc repairs (`src/extensions/Markdown.js`, `src/nodes/Image.js`, `src/nodes/ImageInline.js`, `src/nodes/Table/markdown.ts`, all switching `@tiptap/pm/markdown` → `prosemirror-markdown`) are never imported by either spec, so the tests pass on P⊕Δm without Δc.

## 5. Coverage verdict
UNWITNESSED — the two Δt specs exercise `links.js` (unchanged by Δc) and import `schema` from the newly-added `prosemirror-schema-basic` dep; they never touch the four `@tiptap/pm/markdown`-importing files that Δc repairs, so the hidden tests pass on P⊕Δm without Δc.

## 6. Δc nature
REAL_SOURCE_REPAIR — four source files changed (`src/extensions/Markdown.js`, `src/nodes/Image.js`, `src/nodes/ImageInline.js`, `src/nodes/Table/markdown.ts`), each switching `MarkdownSerializer`/`defaultMarkdownSerializer`/`MarkdownSerializerState` imports from `@tiptap/pm/markdown` to the standalone `prosemirror-markdown` package. No docs, config, or snapshots.

## 7. Soundness concerns / notes
- Confirmed by the 2026-06-10 review: "Source-looking but unwitnessed."
- The Δc repair (markdown serializer imports) is real and motivated by @tiptap/pm 3.22.4 dropping the markdown re-export, but Δt only fixes the `schema-basic` import in tests and exercises an unrelated plugin (`links.js`) — coverage gap means the source repair is not witnessed.
- A witnessing Δt would have added a spec importing `Markdown.js`/`Image.js`/`Table/markdown.ts` so the broken `@tiptap/pm/markdown` import would surface; instead Δt avoids those modules entirely.
