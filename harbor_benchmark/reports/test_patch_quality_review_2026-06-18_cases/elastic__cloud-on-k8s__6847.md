# Test-patch audit — elastic__cloud-on-k8s__6847

## 1. Task summary
- Folder: elastic__cloud-on-k8s__6847
- Ecosystem: go_modules
- Upgrade: k8s.io/api 0.26.5 -> 0.27.2 (plus k8s.io/apimachinery/client-go 0.27.2 and controller-runtime 0.15.0)
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `go test ./pkg/utils/test ./test/e2e/test/elasticsearch ./test/e2e/test/logstash`

## 2. What is the breaking change?
The Kubernetes/controller-runtime upgrade pulls in controller-runtime 0.15 APIs. Several compile-facing APIs used by this repo changed: `webhook.Validator` validation methods now return `(admission.Warnings, error)` instead of just `error`; `admission.ValidatingWebhookFor` now takes the scheme directly; `admission.NewDecoder` no longer returns an error; controller watches now use `source.Kind(cache, obj)` and function-style `handler.EnqueueRequestForOwner`; event handlers and map funcs receive `context.Context`; and manager webhook/cache options moved from `CertDir`/`Port`/`NewCache` to `WebhookServer`/`Cache.Namespaces`.

## 3. What does Δt (test.patch) actually do?
- `pkg/utils/test/webhook.go`: updates the shared validation-webhook test helper from `admission.ValidatingWebhookFor(validator)` plus `InjectScheme`/`InjectLogger` to `admission.ValidatingWebhookFor(clientgoscheme.Scheme, validator)`, and removes the now-unused test logger import/variable.
- `test/e2e/test/elasticsearch/checks_reversal.go`: renames an unused method parameter from `k` to `_`.
- `test/e2e/test/logstash/http_client.go`: renames an unused function parameter from `k` to `_`.

No new behavioral assertion is added. The load-bearing Δt hunk is the webhook helper migration to the new controller-runtime admission API; the two `_` parameter edits are non-load-bearing for `go test`.

## 4. Does Δt directly exercise the breaking change?
Yes, primarily as a compile witness. With Δm and Δt applied, the verifier compiles `pkg/utils/test` against the new `admission.ValidatingWebhookFor(clientgoscheme.Scheme, validator)` API and then compiles the Elasticsearch/Logstash e2e packages and their imports against controller-runtime 0.15. The old source validators still have methods like:

```go
func (es *Elasticsearch) ValidateCreate() error
```

but controller-runtime 0.15 expects:

```go
func (es *Elasticsearch) ValidateCreate() (admission.Warnings, error)
```

The old source also still uses removed/changed controller-runtime watch forms such as `&source.Kind{Type: ...}` and struct-literal `handler.EnqueueRequestForOwner`. Those are compile failures under the upgraded dependencies. Δc repairs these by updating every CRD validator signature, changing call sites to ignore the warning return (`_, err := obj.ValidateCreate()`), migrating watch/event-handler APIs, and moving manager webhook/cache configuration to the new option fields.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — this is a compile-level witness for the controller-runtime/Kubernetes API break introduced by the dependency bump. `TEST(P⊕Δm⊕Δt)` fails because the source still implements the old validator/watch/handler APIs, while `TEST(P⊕Δm⊕Δc⊕Δt)` compiles and runs with the new controller-runtime 0.15 API shape.

## 6. Δc nature
MIXED — Δc contains substantial real source repairs (`cmd/manager/main.go`, all `pkg/apis/*/webhook.go`, controller watch setup, dynamic watch handlers, fake client helpers, webhook handlers), but it is bundled with many non-source or test-side changes: generated CRD YAML, `NOTICE.txt`, dependency documentation, and numerous `*_test.go` updates from `runtime.Object` to `client.Object` / new helper signatures. The core repair is real source migration, but the patch is not source-only.

## 7. Soundness concerns / notes
- The hidden Δt is small and does not add a new behavioral assertion; it mostly makes the verifier-side webhook helper compile against the new dependency.
- The verdict is still witnessed because the failure mode is a legitimate compile break from removed/changed upstream APIs, not dependency resolution, network, OOM, flaky behavior, timeout, or lint.
- Δc is much broader than the hidden test command. The verifier strongly witnesses the controller-runtime API migration needed for compile, but it does not independently cover all generated CRD/docs/test churn in the upstream repair patch.
