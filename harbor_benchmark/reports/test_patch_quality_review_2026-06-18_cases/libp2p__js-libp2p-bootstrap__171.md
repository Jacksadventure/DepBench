# Test-patch audit — libp2p__js-libp2p-bootstrap__171

## 1. Task summary
- Folder: libp2p__js-libp2p-bootstrap__171
- Ecosystem: npm_and_yarn
- Upgrade: @libp2p/interface-peer-store 1.2.2 -> 2.0.0
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `npx aegir test -t node`

## 2. What is the breaking change?
The libp2p peer-store interface changed: bootstrap can no longer rely on the old `tagPeer`/`getTags` shape, and event dispatch should use the current libp2p `EventEmitter` helper instead of constructing a `CustomEvent` import from the old events package.

## 3. What does Δt (test.patch) actually do?
The tests replace real `PersistentPeerStore` setup with a `sinon-ts` stub of the new `PeerStore` interface. The bootstrap test now asserts that `peerStore.merge(peerId, { tags: ... })` is called with the expected tag payload, and compliance tests pass a stubbed peer store.

## 4. Does Δt directly exercise the breaking change?
Yes. With Δm and Δt but without Δc, source still calls `peerStore.tagPeer(...)` and imports/dispatches through the old event shape. The hidden test expects the new `merge` contract and the upgraded types should reject or fail the old method usage. Δc switches to `peerStore.merge` and `safeDispatchEvent`.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — the hidden tests directly target the peer-store v2 contract used by the production bootstrap implementation.

## 6. Δc nature
REAL_SOURCE_REPAIR — Δc is a focused production TypeScript source change in `src/index.ts`.

## 7. Soundness concerns / notes
The rewritten tests mock the peer store rather than exercising a real `PersistentPeerStore`, so they verify the new interface call shape more than end-to-end tag expiration behavior. That is appropriate for this API migration.
