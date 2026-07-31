# Zero-pass contract audit repairs

Date: 2026-07-31

## Scope

Reviewed the D1-D6 defect classes and the oracle-failing tasks identified by the
2026-07-29 manual zero-pass audit. The canonical release remains an end-to-end
dependency-upgrade benchmark. Manifest pre-application for the 14 specifically
identified tasks is implemented only in the MSBench variant.

## Canonical changes

- Hardened all 203 verifier bootstrap scripts so apt/curl/uv failures stop the
  verifier instead of silently writing reward 0.
- Disclosed required sibling upgrades for Algolia 305, GraphQL Tools 7001,
  libp2p bootstrap 171, and Nextcloud Spreed 6266.
- Repaired the Base65536 exact-version gate, hidden no-save installs, verifier
  exception paths, and the Dropshot 630 build timeout.
- Repaired the audited oracle contracts for 29k 5244, Jsonschema 825,
  mjml_nif 117/13, Cryostat 1880, Decap CMS 5178, SQLFrame 581/589,
  cloud-on-k8s 6847, Hellodata 315, and Operaton 1523.

Canonical commit:
`907c2800eac673455066754454508f3ac2bd1ad3`

Pushed to both `origin/v4-with-test` and
`Jacksadventure/DepBench@v4-with-test`.

Oracle validation:

- Config: `_run_configs/oracle_zero_pass_repairs_20260731.yaml`
- Job: `harbor_jobs/2026-07-31__05-21-04`
- Result: 20/20 reward 1, no exceptions

## Distribution

Hugging Face:

- Repository: `ZijiantheJack/DepBench`
- Revision: `e674c1053ff15f67b1b7f47be0985a7b0cd29b07`
- Archive SHA256:
  `2f5207ce8a73a31d812839b853728d54d117c19829aa3d5a8f631388af52d076`
- All 203 instructions passed the bump audit.
- No public instruction mentions `manifest.patch` or says that the upgrade has
  not been applied.

Release:

- Commit: `3aeb7f450ae195d48d195ff3c395b6df84e4fe57`
- Pushed to both GitHub `main` remotes.

MSBench:

- Commit: `9425e75462ca27f7ef9b505cfada4bccd6c78e4d`
- Branch: `depbench/affected56-sync-20260727`
- PR: `764901`
- The 14 requested tasks have an MSBench pre-agent hook, an empty solution
  manifest patch, and explicit pre-applied wording. The canonical/HF copies do
  not.
- All 14 hooks were tested in their real images and passed.
- The generated dataset has 203 rows and all 203 verifiers carry the hardened
  bootstrap behavior.

