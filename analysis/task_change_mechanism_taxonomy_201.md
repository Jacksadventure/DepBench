# Task Change Mechanism Classification (201 Tasks)

## Classification rule

Classify by the dominant oracle-repair mechanism. Direct means the first-order dependency's visible package/API/signature/type surface changed. Indirect means behavior, dependency resolution, configuration/tooling, or generated output changed without a primary first-order API surface break.

Each task receives one mutually exclusive primary label. Mixed tasks are
classified by the mechanism that dominates the oracle repair.

## Direct vs. indirect

| Scope | Tasks | Share |
| --- | ---: | ---: |
| Direct | 142 | 70.6% |
| Indirect | 59 | 29.4% |
| Total | 201 | 100.0% |

## Primary mechanisms

| Scope | Mechanism | Tasks | Share |
| --- | --- | ---: | ---: |
| Direct | `package-module-namespace` | 33 | 16.4% |
| Direct | `api-symbol-removal-rename` | 46 | 22.9% |
| Direct | `function-signature-calling-convention` | 27 | 13.4% |
| Direct | `type-interface-schema` | 36 | 17.9% |
| Indirect | `runtime-semantic-behavior` | 20 | 10.0% |
| Indirect | `dependency-chain-resolution` | 6 | 3.0% |
| Indirect | `configuration-build-tooling` | 18 | 9.0% |
| Indirect | `generated-output-data-contract` | 15 | 7.5% |

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
`analysis/task_change_mechanism_classification_201.csv`.
