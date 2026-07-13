# Case study: python-telegram-bot__python-telegram-bot__4024 (httpx 0.25.2 → 0.26.0)

**Split:** gpt55 3/3 PASS (codex, claude_code, opencode) vs claude48 0/3 FAIL (claude_code [guarded replacement of an original 1.0], copilot_cli, opencode). gemini35flash: claude_code PASS, other two fail (one no-trajectory).

**Headline finding:** This is NOT a "silent breakage / context-acquisition laziness" task. Every claude48 run found the breaking change (`bc_hyp=True` for all three in
`harbor_benchmark/reports/v4_withtest219_trajectory_behavior_unified_20260627.csv`). The task is an **adversarial oracle-inference trap**: the *visible* tests assert the OLD `proxies` kwarg, while the *hidden* graded tests assert the NEW `proxy` kwarg. claude48 anchored on the visible tests as the oracle (as the instruction literally suggests) and preserved `proxies`; gpt55 hedged with a dual-kwarg adapter that satisfies both. The split is a difference in **decision rule under oracle ambiguity**, not knowledge or effort.

---

## 1. Ground truth

Human repair (`harbor_benchmark/tasks_v4/.../solution/code.patch`), in `telegram/request/_httpxrequest.py`:

```diff
         self._client_kwargs = {
             "timeout": timeout,
-            "proxies": proxy,
+            "proxy": proxy,
```

(plus pin/docs bumps in requirements.txt, .pre-commit-config.yaml, README*.rst). httpx 0.26.0 deprecated the `proxies=` argument of `Client`/`AsyncClient` in favor of `proxy=` (removed later in 0.28); upstream PTB PR #4024 did the rename.

Hidden tests (`tests/test.patch`) rewrite the mock in both test files to the post-upgrade shape:

```diff
         @dataclass
         class Client:
             timeout: object
-            proxies: object
+            proxy: object
...
-        assert request._client.proxies is None
+        assert request._client.proxy is None
-        assert request._client.proxies == "proxy"
+        assert request._client.proxy == "proxy"
```

Grading (`tests/test_state.py`) applies the patch and runs exactly three tests:
`test_applicationbuilder.py::...::test_default_values`, `...::test_all_bot_args_custom`, `test_request.py::TestHTTPXRequestWithoutRequest::test_init`.
Because the hidden mock is a fixed-signature dataclass with field `proxy`, any solution still passing `proxies=` dies with `TypeError: unexpected keyword argument 'proxies'`.

**The trap:** the visible (pre-upgrade) tests assert the exact opposite — `tests/request/test_request.py:438 proxies: object`, `:448 assert request._client.proxies is None`, `:464 assert request._client.proxies == "proxy"`. A clean rename to `proxy` makes the visible suite FAIL. The instruction tells agents: *"Do not modify any test files. The test suite is the evaluation oracle and will be re-applied verbatim before grading"* and *"...so that the existing tests pass"* — which, read literally against the visible tree, argues for keeping `proxies`.

**Signals available (not silent):**
- The container shipped httpx **0.28.1** (not 0.25.2 or 0.26.0), where `proxies` is *removed* → running visible tests immediately yields `TypeError: AsyncClient.__init__() got an unexpected keyword argument 'proxies'` (seen by claude48/claude_code, step 31).
- After installing 0.26.0, the visible test `test_proxy_url_deprecation_warning` fails with `assert 2 == 1` because httpx 0.26 adds its own `DeprecationWarning: The 'proxies' argument is now deprecated. Use 'proxy' or 'mounts' instead.` (seen by claude48/copilot_cli step 21 and claude48/opencode step 19; notably it did NOT reproduce in claude48/claude_code's run, which saw `1 failed, 53 passed, 1 skipped` with only the network-dependent HTTP/2 test failing).

## 2. Why the claude48 configs failed

### claude48/claude_code (22k chars, guarded replacement; original unguarded run scored 1.0)
Found the 0.28.1 TypeError, then **downgraded to 0.26.0 and re-tested — the visible suite went green** ("1 failed, 53 passed" with the failure being the network-only `test_http_2_response`, "All connection attempts failed"). Final decision (step 53):

> "**No source code changes were needed.** The `proxies=` keyword argument used in `telegram/request/_httpxrequest.py` remains valid in httpx 0.26.0 (it wasn't removed until httpx 0.28.x). ... Installed httpx 0.26.0 and ran `tests/request/test_request.py` — 53 passed, 1 skipped."

Only edit: `requirements.txt` pin. It never registered the 0.26 *deprecation* (its env didn't surface the 2-warnings failure) and exited early on green visible tests. The original 1.0 run this replaced (see `guarded_leak_remaining_claude_replacement_audit_20260702.csv`: original_reward 1.0 → new_reward 0) very likely reached the rename via upstream access, which the guards then blocked.

### claude48/opencode (104k chars, native)
Fully diagnosed everything — deprecation, the recwarn failure, even the exact conflict:

> Step 19: "The fix: httpx 0.26.0 introduced a new `proxy` parameter ... I need to change the source from passing `proxies=` to `proxy=`. **But wait — the OTHER tests (test_init, test_default_values) mock the client with a `proxies` field** ..."
> Step 21: "the test passes `proxies` field — **the source MUST send `proxies=`**. To avoid the real httpx deprecation warning ... the source must suppress that specific httpx `DeprecationWarning`."

Final solution: keep `"proxies": proxy` and wrap `_build_client` in `warnings.catch_warnings()` suppression. Visible suites green (54 + 170 passed) → reward 0 (hidden mock has no `proxies` field).

### claude48/copilot_cli (28k chars, native)
Same suppression fix, but with the most damning evidence: its instruction version had **no upstream-access ban**, and it actually researched GitHub and learned the truth —

> Step 63: "The OFFICIAL PR #4024 ... **renamed the kwarg from `proxies` to `proxy` and updated their tests accordingly.**"

— then reasoned itself out of it:

> Step 63: "The local tests still use `proxies` ... This means the hidden tests in /app are a *custom/modified* variant, and the 'suppress the warning' approach is what's needed here — NOT the upstream rename."

It compounded this by mistaking its *own earlier edit* for pre-existing canonical code (step 70: "the on-disk file ALREADY contains the exact verbatim solution ... PTB later **reverted to `proxies`** and added the `catch_warnings` suppression" — a hallucinated history). Earlier framing (step 15): "The test mocks `AsyncClient` with a `proxies` field ... **The test is the oracle.**"

## 3. What the gpt55 passers did differently

Neither passer trusted the visible mocks as the final oracle; both treated them as possibly-stale doubles and **hedged with an adaptive dual-kwarg strategy**:

- **gpt55/codex** (step 15): "The tests in this checkout still model the old `proxies` keyword, while the installed runtime no longer accepts it. I'm going to make the source **choose the supported keyword from the active `httpx.AsyncClient`**, which keeps old test doubles working and fixes real newer httpx." Verified against both installed httpx and an isolated `httpx==0.26.0` import path (224 passed both ways).
- **gpt55/claude_code**: "some tests monkeypatch `AsyncClient` with older-style `proxies` signatures. I'm going to make the production path use `proxy` and add a narrow fallback for older/fake clients that reject only that keyword." Implemented exactly:

```python
def _build_client(self) -> httpx.AsyncClient:
    try:
        return httpx.AsyncClient(**self._client_kwargs)   # primary: "proxy"
    except TypeError as exc:
        if ... "unexpected keyword argument 'proxy'" not in str(exc): raise
        client_kwargs = self._client_kwargs.copy()
        client_kwargs["proxies"] = client_kwargs.pop("proxy")
        return httpx.AsyncClient(**client_kwargs)
```

This passes the visible mock (`proxies` field → TypeError → fallback), the hidden mock (`proxy` field → primary path), AND real httpx 0.26 (primary path, no deprecation warning → `test_proxy_url_deprecation_warning` sees exactly 1 warning). They did not need the changelog per se — the preinstalled 0.28.1's hard TypeError plus model knowledge of the rename sufficed; the differentiator was making the **modern kwarg the primary path** instead of the legacy one.

## 4. Is this "silent breakage"?

**No.** The breakage was loud twice over (0.28.1 TypeError out of the box; `assert 2 == 1` recwarn failure under 0.26.0 in two of three claude48 runs). All claude48 runs formed the correct breaking-change hypothesis (bc_hyp=True). This task is instead evidence for a different intervention target: **oracle semantics**. The visible tests actively *contradict* the graded fix, and the instruction's "existing tests ... re-applied verbatim" phrasing reinforces the wrong anchor. What separates pass from fail is a policy prior of the form *"the graded suite encodes post-upgrade semantics; visible tests may assert pre-upgrade API shapes — prefer the canonical upstream migration and make it back-compatible, never suppress the dependency's deprecation signal to keep old assertions alive."* A generic "breaking-change card" (facts: proxies→proxy in 0.26) would have been redundant for opencode/copilot_cli — they already knew — though it would likely have flipped claude_code, which explicitly believed `proxies` "remains valid in 0.26.0" and stopped.

## 5. Verdicts

| Run | Classification | Flipping intervention |
|---|---|---|
| claude48/claude_code (guarded) | **Early-exit on green visible tests + partial knowledge gap** (missed the 0.26 deprecation; its env showed no failing signal after the 0.26 downgrade). Also: original 1.0 was leak-assisted; guards removed the crutch. | Breaking-change card ("0.26 deprecates `proxies`→`proxy`; upstream renamed") would flip it; policy prior ("assume the bump breaks something *the visible tests don't show*") also flips it. More time: unlikely — it ended satisfied. |
| claude48/opencode | **Overfit to visible tests** (knowledge complete; explicitly rejected the rename because the visible mock demands `proxies`). | Policy prior / oracle clarification ("hidden graded tests reflect post-upgrade expectations; prefer canonical fix or a both-ways adapter"). A facts-only card would NOT flip it. |
| claude48/copilot_cli | **Overfit + self-confirmation hallucination** (knew the upstream rename from GitHub, dismissed it as "custom variant", mistook its own edit for canonical code). | Same policy prior; card only helps if it states the *oracle direction* (hidden tests assert `client.proxy`), not just the API fact. |

**Meta-lesson for the benchmark:** the instruction sentence "The test suite is the evaluation oracle and will be re-applied verbatim before grading" is actively misleading here — the *patched* (hidden) suite is what is re-applied. gpt55's win is partly a superior prior and partly a hedge (adaptive kwarg) that is robust regardless of which reading is correct; claude48's loss is faithful literalism toward the visible oracle. Any "breaking-change card" intervention for tasks like this must communicate oracle direction ("tests will be upgraded to post-bump semantics"), not merely the changelog entry.

### Sources
- Task assets: `harbor_benchmark/tasks_v4/python-telegram-bot__python-telegram-bot__4024/{instruction.md, solution/code.patch, tests/test.patch, tests/test.sh, tests/test_state.py}`
- Trajectories (extracted): `conversations/260713-half-pass-analysis/trials/python-telegram-bot__python-telegram-bot__4024__{gpt55__codex, gpt55__claude_code, claude48__claude_code, claude48__copilot_cli, claude48__opencode}.json`
- Guarded replacement audit: `harbor_benchmark/reports/guarded_leak_remaining_claude_replacement_audit_20260702.csv` (row `claude_code_claude48, ...4024`: original 1.0 → 0.0)
- Behavior flags: `harbor_benchmark/reports/v4_withtest219_trajectory_behavior_unified_20260627.csv`
