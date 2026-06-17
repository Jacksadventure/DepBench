# Test-patch audit — jenkinsci__kubernetes-plugin__1101

## 1. Task summary
- Folder: jenkinsci__kubernetes-plugin__1101
- Ecosystem: maven
- Upgrade: kubernetes-client-api 5.10.1-171.vaa0774fb8c20 -> 5.11.1-179.v12037658df90
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: Maven `ContainerExecDecoratorTest` command extracted in `tests/test_state.py`

## 2. What is the breaking change?
The Jenkins Kubernetes client API changed around Fabric8 HTTP/WebSocket abstractions. Existing code still used OkHttp-specific access through `HttpClientAware#getHttpClient()` and old `ExecListener.onOpen(Response)` signatures.

## 3. What does Δt (test.patch) actually do?
`ContainerExecDecoratorTest.java` updates imports and expectations for the new client behavior: it expects a `WebSocketHandshakeException` cause, removes OkHttp connection-pool diagnostics, and drops the direct OkHttp import.

## 4. Does Δt directly exercise the breaking change?
Yes. The verifier targets `ContainerExecDecoratorTest`. On P⊕Δm⊕Δt, production code still references removed/changed OkHttp-facing client APIs and old listener signatures, so compilation should fail before or during the targeted test. Δc removes the OkHttp connection-count worker and updates `ExecListener` overrides to the new API.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — the task witnesses a real client API migration through deterministic compile/test compatibility.

## 6. Δc nature
REAL_SOURCE_REPAIR — Δc changes production Java in `KubernetesClientProvider`, `ContainerExecDecorator`, and `SecretsMasker`.

## 7. Soundness concerns / notes
Part of the repair removes a connection-count monitoring extension rather than replacing it, so the task is a compatibility repair with some feature removal. The witness remains source/API compatibility, not lint or infrastructure.
