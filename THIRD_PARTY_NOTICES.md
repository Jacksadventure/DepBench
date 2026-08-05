# Third-Party Notices

DepBench contains or references material originating from third-party source
repositories. Microsoft does not relicense that material under the repository's
MIT license.

## Benchmark data and research artifacts

The 201 tasks distributed from `main` originate from 157 repositories. The complete
repository URL, detected license, license source, primary language, task count,
and task mapping are recorded in:

- `analysis/repository_metadata.csv`
- `analysis/repository_metadata.json`
- `analysis/task_repository_metadata.csv`

Users must review the license and other terms of each source repository before
redistributing or using a task, source excerpt, patch, or derived artifact.
Upstream licenses and notices remain controlling for upstream material.

The current metadata classifies 192 tasks as originating from open-source
repositories. The following 9 tasks require additional review because their
repositories use source-available or custom terms:

| Repository | Identifier | Category | Tasks |
|---|---|---|---:|
| Graylog2/graylog2-server | SSPL-1.0 | source-available | 3 |
| elastic/cloud-on-k8s | Elastic-2.0 | source-available | 2 |
| liquibase/liquibase | FSL-1.1-ALv2 | source-available | 1 |
| mitre/heimdall2 | LicenseRef-Apache-2.0-with-MITRE-terms | custom | 1 |
| opengovsg/askgovsg | LicenseRef-MIT-with-GovTech-terms | custom | 1 |
| sourcenetwork/defradb | BUSL-1.1 | source-available | 1 |

The `databricks/cli` and `nearform/brokeneck` tasks are excluded from the
`main` distribution. Their upstream pull requests remain linked in the README
so users can independently reconstruct the upgrades subject to upstream terms.

This inventory is descriptive and is not legal advice or a substitute for
Open Data and OSSOM CELA review.

## Runtime dependencies

The helper package declares Harbor and `huggingface-hub` as runtime
dependencies. These packages are not vendored in this repository and remain
subject to their own licenses and notices. Agent CLIs, Docker images, package
registries, model providers, and source repositories reached during a run are
also third-party services or software governed by their respective terms.
