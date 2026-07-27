# Task Change Mechanism Classification (203 Tasks)

## Classification rule

Classify by the dominant oracle-repair mechanism. Direct means the first-order dependency's visible package/API/signature/type surface changed. Indirect means behavior, dependency resolution, configuration/tooling, or generated output changed without a primary first-order API surface break.

Each task receives one mutually exclusive primary label. Mixed tasks are
classified by the mechanism that dominates the oracle repair.

## Direct vs. indirect

| Scope | Tasks | Share |
| --- | ---: | ---: |
| Direct | 144 | 70.9% |
| Indirect | 59 | 29.1% |
| Total | 203 | 100.0% |

## Primary mechanisms

| Scope | Mechanism | Tasks | Share |
| --- | --- | ---: | ---: |
| Direct | `package-module-namespace` | 33 | 16.3% |
| Direct | `api-symbol-removal-rename` | 47 | 23.2% |
| Direct | `function-signature-calling-convention` | 27 | 13.3% |
| Direct | `type-interface-schema` | 37 | 18.2% |
| Indirect | `runtime-semantic-behavior` | 20 | 9.9% |
| Indirect | `dependency-chain-resolution` | 6 | 3.0% |
| Indirect | `configuration-build-tooling` | 18 | 8.9% |
| Indirect | `generated-output-data-contract` | 15 | 7.4% |

## Definitions

- **Direct / `package-module-namespace`:** Package, module, import path, namespace, or export relocation.
- **Direct / `api-symbol-removal-rename`:** A dependency API symbol was removed, renamed, or replaced.
- **Direct / `function-signature-calling-convention`:** Arguments, return values, constructors, sync/async use, or call protocol changed.
- **Direct / `type-interface-schema`:** A dependency-exposed type, interface, field, generic, or schema shape changed.
- **Indirect / `runtime-semantic-behavior`:** The callable surface remained usable but runtime meaning or behavior changed.
- **Indirect / `dependency-chain-resolution`:** A transitive dependency, resolution result, bundled component, or interaction changed.
- **Indirect / `configuration-build-tooling`:** Configuration, compiler/linter policy, build system, test runner, or packaging changed.
- **Indirect / `generated-output-data-contract`:** Generated code, serialized data, SQL, formatting, snapshots, or textual output changed.

## Evidence and caveat

The labels were reviewed against the dependency metadata, oracle repair
patch, and hidden-test/verifier witness. They describe the primary repair
mechanism, not every secondary effect present in a task.

The task-level labels are in
`analysis/task_change_mechanism_classification_203.csv`.
