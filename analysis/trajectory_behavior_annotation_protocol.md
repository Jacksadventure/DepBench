# Final Trajectory Behavior Annotation Protocol

Table 7 is derived from one behavior annotation for each of the 2,030 final
configuration-task trajectories. The four labels are non-exclusive:

- `docs_lookup`: the agent accessed dependency documentation, release notes,
  changelog, or migration material. Own-project documentation, registry
  metadata, printed URLs, plans, and unsuccessful searches do not count.
- `api_source_inspection`: the agent inspected dependency API, source, type
  declarations, installed package contents, module caches, JAR classes, or
  runtime exports. Project source, manifests, and lockfiles alone do not count.
- `ran_tests`: the agent executed a test, build, typecheck, or compile command.
  Plans to run a command do not count.
- `bc_hypothesis`: the agent explicitly stated a concrete dependency API or
  semantic change. Generic breakage statements and changes inferred only from
  edits or compiler output do not count.

The final artifact preserves 1,627 existing repository-schema annotations whose
task and trial identifiers exactly match the selected final trajectories. The
remaining 403 replacement or previously uncovered trajectories were annotated
once from their complete serialized trajectories with the same definitions.
Each JSONL row records its `annotation_source`, `annotator`, confidence, and a
short evidence rationale.

`repro/summarize_trajectory_behavior_annotations.py` verifies exact coverage of
the final trajectory keys and regenerates the configuration and provenance
summaries used for the paper.
