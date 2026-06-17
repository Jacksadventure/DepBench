# Test-patch audit — elastic__cloud-on-k8s__3417

## 1. Task summary
- Folder: elastic__cloud-on-k8s__3417
- Ecosystem: go_modules
- Upgrade: k8s.io/api 0.17.2 -> 0.18.4 (with k8s.io/apimachinery/client-go/controller-runtime bumps)
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `go test ./test/e2e/cmd/run ./test/e2e/test/apmserver`

## 2. What is the breaking change?
The Kubernetes Go client API changed to context-aware method signatures in this version range. Calls such as `Pods(...).Get(name, opts)`, `Secrets(...).Update(obj)`, `SubjectAccessReviews().Create(obj)`, REST `Do()`, and log `Stream()` now require `context.Context` and explicit create/update options.

## 3. What does Δt (test.patch) actually do?
It updates two e2e test/helper files in the verifier scope:
- `test/e2e/cmd/run/run.go`: changes pod `Get` to `Get(context.Background(), podName, metav1.GetOptions{})` and log streaming from `.Context(...).Stream()` to `.Stream(context.Background())`.
- `test/e2e/test/apmserver/steps_creation.go`: imports `context` and changes `patchClient.Do()` to `patchClient.Do(context.Background())`.

## 4. Does Δt directly exercise the breaking change?
Yes. The hidden tests themselves must compile against the new client-go signatures, and the tested packages import the operator/test support code that Δc migrates. On P⊕Δm, the old source still contains many pre-0.18 Kubernetes client calls and fails to compile; with Δc, those calls are migrated to context-aware forms and the updated e2e packages compile.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — the failure is a Go compile break caused by the Kubernetes API signature changes, not dependency resolution, lint, network, or timeout behavior.

## 6. Δc nature
MIXED — substantial real source repair across operator/controller/dev packages, plus generated CRD/docs dependency updates and in-repo test adjustments.

## 7. Soundness concerns / notes
The task is valid as a compile-error witness, but Δc is broad and includes generated artifacts and tests outside the verifier command. The core discriminating repair is the context/options migration in production code.
