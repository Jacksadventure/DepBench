*(Note: After an exhaustive local filesystem search across workspace, user, and scratch directories, the explicitly requested local source files were not found. I have designed this proposal grounded directly in the provided prompt constraints, the DepBench paper diagnoses cited, and domain expertise regarding agentic software engineering.)*

### Critique of the Current Direction
The prevailing strategy of simply indexing and retrieving more text (PR histories, World of Code, documentation) fundamentally misdiagnoses the failure mode. According to the July 13 diagnosis, agents already successfully inspect documentation and local APIs. Their failure stems from **scope myopia**: they treat dependency upgrades like localized bug fixes rather than repository-wide contract changes. Consequently, they stop as soon as the local visible tests pass, resulting in a devastating 46.8% false-positive rate where hidden verification fails. Adding more retrieved text will only bloat the context window without altering the agent's premature stopping behavior. We must shift the architecture from *context retrieval* to *contract propagation and adversarial validation*.

Here is the decision-complete architecture and experiment for the prototype and empirical study:

---

### 1. Product/Research Thesis and Falsifiable Hypotheses
**Thesis:** Providing documentation to an agent is insufficient for dependency upgrades. To succeed, the agent must be forced to explicitly reconstruct the upstream breaking changes, map them strictly to repository-wide call graphs, and actively synthesize adversarial test suites that invalidate the false "visible-test pass" state before any code is modified.
**Falsifiable Hypotheses:**
*   **H1 (Propagation):** Forcing the agent to emit a declarative "Contract Change Graph" prior to implementation will increase repository-wide propagation success by >30% compared to standard zero-shot or ReAct baselines on the 79 npm tasks.
*   **H2 (Stopping Criteria):** Requiring the agent to write failing local tests for the upgraded dependency before modifying application code will reduce the "visible-test pass -> hidden verification failure" rate from 46.8% to <15%.

### 2. Mining/Indexing/Retrieval Architecture & Artifact Schemas
The architecture must operate strictly offline to enforce time-travel boundaries before agent execution.
*   **Miner Pipeline:** Given `(package, from_v, to_v, cutoff_timestamp)`, the miner queries World of Code (WoC) and GHArchive for all repositories that performed this exact upgrade *before* the cutoff. It extracts PR diffs, same-organization history, and upstream releases/tests.
*   **Versioned Artifact Schemas:**
    *   `UpstreamChange`: `{ pkg_name, from_v, to_v, breaking_signatures: List[str], migration_hints: List[str] }` *(Generated from upstream diffs)*
    *   `ExternalEvidence`: `{ source_repo, commit_hash, before_snippet, after_snippet, context_intent }` *(Mined from GHArchive/WoC)*
    *   `LocalContractMap`: `{ file_path, imported_symbols, line_numbers, dependent_files }` *(Agent-generated)*

### 3. Agent Loop, Authority Ordering, and Stop Conditions
The standard ReAct loop must be heavily constrained by a strict authority hierarchy and completeness checks to prevent premature stopping.
*   **Authority Ordering & Contradiction Handling:**
    *   *Hierarchy:* Upstream Source Diffs > Upstream Docs > External PR Evidence > Local Visible Tests.
    *   *Handling:* If external PR evidence from WoC contradicts upstream documentation, trust the source code diffs. If visible tests pass but the `LocalContractMap` indicates a dependent file hasn't been touched, the map overrides the visible tests.
*   **The Re-baselined Agent Loop:**
    1.  **Contract Mapping:** Synthesize retrieved artifacts and output the `LocalContractMap` (a definitive list of all files requiring edits).
    2.  **Adversarial Testing:** Write a failing test exposing the breaking change in the local codebase.
    3.  **Implem...
