# Test-patch audit — python-telegram-bot__python-telegram-bot__4024

## 1. Task summary
- Folder: python-telegram-bot__python-telegram-bot__4024
- Ecosystem: pip
- Upgrade: httpx 0.25.2 -> 0.26.0
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `pytest tests/ext/test_applicationbuilder.py::TestApplicationBuilder::test_default_values tests/ext/test_applicationbuilder.py::TestApplicationBuilder::test_all_bot_args_custom tests/request/test_request.py::TestHTTPXRequestWithoutRequest::test_init -v`

## 2. What is the breaking change?
httpx 0.26 changes the client proxy keyword from `proxies` to `proxy`. `telegram.request.HTTPXRequest` passed `proxies`, so constructing the HTTPX client with the upgraded dependency would fail or expose the wrong captured argument in the tests.

## 3. What does Δt (test.patch) actually do?
- Updates monkeypatched `Client` dataclasses in application-builder and request tests from a `proxies` field to a `proxy` field.
- Updates assertions from `client.proxies` to `client.proxy`, including default `None`, `"proxy"`, and `"get_updates_proxy"` cases.
- Adds temporary warning prints in one request test, but the selected verifier tests focus on HTTPXRequest initialization/application-builder defaults and custom bot args.

## 4. Does Δt directly exercise the breaking change?
Yes. The hidden tests instantiate `HTTPXRequest` and application builders through monkeypatched HTTPX clients that now accept/record `proxy`. On P⊕Δm⊕Δt, production code still sends `proxies`, which no longer matches httpx 0.26's API and the patched tests' expected field. Δc changes the keyword to `proxy`.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — the tests directly assert the post-httpx-0.26 proxy keyword behavior through the real request builder path.

## 6. Δc nature
MIXED — `telegram/request/_httpxrequest.py` is the real source repair, but the patch also updates `.pre-commit-config.yaml` dependency pins and README dependency text.

## 7. Soundness concerns / notes
The core source/test witness is strong. The only impurity is non-source dependency/documentation churn in Δc.
