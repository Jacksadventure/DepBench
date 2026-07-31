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

The later instruction-format cleanup removed the internal
`v3-no-manifest-preapply` HTML marker from all task instructions at commit
`9750bc95f5d0830059346fb1b3f6c947e40cb7d9`. This did not change task
execution semantics.

Oracle validation:

- Config: `_run_configs/oracle_zero_pass_repairs_20260731.yaml`
- Job: `harbor_jobs/2026-07-31__05-21-04`
- Result: 20/20 reward 1, no exceptions

## Distribution

Hugging Face:

- Repository: `ZijiantheJack/DepBench`
- Revision: `678ef766a0dfbe3953557270b2bcbcbac683900c`
- Archive SHA256:
  `8a652fa388bcb8ebe23e3cf9906073cbf3bb2a693586240fa48df3942c95879d`
- All 203 instructions passed the bump audit.
- No public instruction mentions `manifest.patch` or says that the upgrade has
  not been applied.
- No public instruction contains an internal mode marker.

Release:

- Commit: `2b194cf42510db710e8bc506da05b143e4543d8e`
- Pushed to both GitHub `main` remotes.

MSBench:

- Commit: `5ef3263829518d8bf4adb8fde8fd7d099b962424`
- Branch: `depbench/affected56-sync-20260727`
- PR: `764901`
- The 14 requested tasks have an MSBench pre-agent hook, an empty solution
  manifest patch, and explicit pre-applied wording. The canonical/HF copies do
  not.
- All 14 hooks were tested in their real images and passed.
- The generated dataset has 203 rows and all 203 verifiers carry the hardened
  bootstrap behavior.
- The generated instructions contain no internal mode markers. Pre-applied
  tasks retain only the visible sentence describing their checkout state.
