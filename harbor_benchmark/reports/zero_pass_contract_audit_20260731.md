# Zero-pass contract audit (2026-07-31)

This audit rechecked the defect classes reported by the 2026-07-29
zero-pass review against the current 203-task contract.

## Confirmed repairs

- **Verifier bootstrap failures (D1):** all 203 active `tests/test.sh`
  scripts now stop on `apt`, `curl`, or `uv` bootstrap errors. Only a
  completed pytest run writes `reward.txt`, so infrastructure failures are
  no longer silently recorded as task failures.
- **Undisclosed dependency gates (D3):**
  `ardatan__graphql-tools__7001` now discloses the
  `@envelop/live-query` bump, and
  `algolia__react-element-to-jsx-string__305` now discloses the `expect`
  and `jest` bumps required by its verifier.
- **Contradictory version gate (D4):**
  `qntm__base65536__37` consistently requires exact version `2.0.0`.
- **Hidden setup dependencies (D5):**
  `libp2p__js-libp2p-bootstrap__171` and
  `nextcloud__spreed__6266` disclose their additional dependencies and
  include them in the manifest upgrade. The oracle no longer supplies
  undeclared `--no-save` installs. The incorrect hidden
  `@octokit/types@6.0.1` install was removed from
  `octokit__auth-oauth-app.js__137`.
- **Verifier exception paths (D6):**
  `jo-sm__stylelint_d__185` now reports a clean failed assertion when the
  installed TypeScript package is absent.
  `open-telemetry__opentelemetry-go__1872` restores hidden-patch targets
  from the baseline before applying the hidden test patch.
- **Build budget:** `oxidecomputer__dropshot__630` now has a 2400-second
  build timeout, matching its observed valid oracle runtime.

## Oracle-failing task repairs

The following task-specific defects were repaired and are covered by the
targeted oracle validation job:

- `29ki__29k__5244`: tolerate historical manifest-patch context drift.
- `Stranger6667__jsonschema__825`: remove unavailable submodule bootstrap
  and run the relevant vendored workspace test.
- `adoptoposs__mjml_nif__117` and `adoptoposs__mjml_nif__13`: reuse the
  Rust toolchain already present in the image.
- `cryostatio__cryostat-legacy__1880`: skip the unrelated Node/Yarn
  frontend bootstrap during Maven verification.
- `decaporg__decap-cms__5178`: restore the missing final newline in both
  manifest patch copies.
- `eakmanrq__sqlframe__581`: install the verifier's missing runtime
  dependency and pin the compatible `sqlglot` line in the oracle.
- `eakmanrq__sqlframe__589`: create the project virtual environment before
  verification.
- `elastic__cloud-on-k8s__6847`: use the Go toolchain path explicitly.
- `kanton-bern__hellodata-be__315`: exclude unrelated environment-bound
  integration tests from the dependency-upgrade verifier.
- `operaton__operaton__1523`: apply oracle patch paths independently when
  the image already contains one hunk.

Validation job: `harbor_jobs/2026-07-31__05-21-04`.

Result: **20/20 passed, with 0 verifier exceptions**. This validation
included every task changed for D3-D6, the repaired oracle-failing tasks,
and the raised-timeout Dropshot task.

## Distribution policy

The canonical release and Hugging Face export remain end-to-end tasks.
Their instructions contain only the dependency bump and constraints; they
do not claim that a `manifest.patch` file is available to the agent.

The following 14 tasks are added to the MSBench manifest-preapply set only:

- `BramVR__gohealthcli__351`
- `Nextdoor__vigil__35`
- `giantswarm__mcp-prometheus__165`
- `giantswarm__muster__751`
- `github__github-mcp-server__412`
- `matt-riley__hopcli__47`
- `score-spec__score-aca__16`
- `shuntaka9576__gh-kanban__16`
- `stackitcloud__stackit-cert-manager-webhook__94`
- `syou6162__times_esa_mcp_server__22`
- `thegeeklab__wp-docker-buildx__349`
- `thegeeklab__wp-opentofu__166`
- `ubugeeei-prod__ox-content__131`
- `xMoelletschi__renoglaab__30`

MSBench rewrites these generated instructions to say that the manifest
upgrade has already been applied. No such wording is shipped in the
canonical release or Hugging Face dataset.
