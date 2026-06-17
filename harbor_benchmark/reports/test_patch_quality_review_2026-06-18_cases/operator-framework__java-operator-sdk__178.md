# Test-patch audit — operator-framework__java-operator-sdk__178

## 1. Task summary
- Folder: operator-framework__java-operator-sdk__178
- Ecosystem: maven
- Upgrade: openshift-client 4.10.3 -> 4.11.0
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `TEST_CMD_UNEXTRACTABLE`

## 2. What is the breaking change?
Fabric8/OpenShift 4.11 moves the CRD model import to the `apiextensions.v1beta1` package and changes custom-resource client creation to use `CustomResourceDefinitionContext` rather than passing a `CustomResourceDefinition` directly. Old code still imports the old CRD class and calls `k8sClient.customResources(crd, ...)`.

## 3. What does Δt (test.patch) actually do?
`operator-framework/src/test/java/com/github/containersolutions/operator/IntegrationTestSupport.java` updates the test helper to import `io.fabric8.kubernetes.api.model.apiextensions.v1beta1.CustomResourceDefinition`, create `CustomResourceDefinitionContext.fromCrd(crd)`, and pass that context into `k8sClient.customResources(...)`.

## 4. Does Δt directly exercise the breaking change?
Yes. With openshift-client 4.11, the hidden test helper uses the new CRD package and `CustomResourceDefinitionContext` API. P⊕Δm source still uses the old production `Operator` imports and custom-resource client call, so compilation fails; Δc applies the same API migration in `Operator.java`.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — the test patch and source patch both target the Fabric8 custom-resource API migration, and the failure is a valid Java compile/API failure.

## 6. Δc nature
REAL_SOURCE_REPAIR — `operator-framework/src/main/java/com/github/containersolutions/operator/Operator.java` is migrated to the v1beta1 CRD model plus `CustomResourceDefinitionContext`.

## 7. Soundness concerns / notes
The bundle metadata could not extract a compact verifier command, but `test_state.py` contains a generated Maven invocation targeting `IntegrationTestSupport`/module tests. The static witness is compile-level and clear.
