# Test-patch audit — peopledatalabs__peopledatalabs-python__132

## 1. Task summary
- Folder: peopledatalabs__peopledatalabs-python__132
- Ecosystem: pip
- Upgrade: annotated-types 7.4.4 -> 7.5.1
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `/usr/local/bin/python -m pytest -k 'not test_api_endpoint_'`

## 2. What is the breaking change?
No dependency-level breaking change is visible in the oracle. The manifest patch bumps a large lockfile set including `annotated-types`, but the oracle source patch only changes the package `__version__` from `3.0.9` to `3.0.10`.

## 3. What does Δt (test.patch) actually do?
- `tests/client/test_client.py`: updates `test_version` to expect `__version__ == "3.0.10"`.
- Several sandbox API endpoint tests change fixture values (`email`, `company`, and `location_country`), but the verifier command excludes `test_api_endpoint_` tests with `-k 'not test_api_endpoint_'`.

## 4. Does Δt directly exercise the breaking change?
No. The only reachable hidden-test change is the version-string assertion. That is release metadata, not behavior affected by `annotated-types` 7.5.1. The sandbox endpoint fixture edits are not run by the verifier.

## 5. Coverage verdict
TESTS_OTHER_THING — the verifier checks package version metadata (`3.0.10`) rather than a dependency-upgrade break. A failure on P⊕Δm⊕Δt would be `assert "3.0.9" == "3.0.10"`, not evidence that `annotated-types` broke source behavior.

## 6. Δc nature
CONFIG_INFRA_ONLY — `src/peopledatalabs/__init__.py` changes only the exported package version string.

## 7. Soundness concerns / notes
- The hidden test can be satisfied by changing a version constant only.
- The dependency under audit is not exercised by the verifier, and the API endpoint fixture changes are excluded by the test selector.
