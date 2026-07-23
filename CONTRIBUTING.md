# Contributing to DepBench

This repository welcomes bug reports, documentation improvements, benchmark
contract corrections, and reproducibility fixes.

## Before opening a pull request

1. Create an issue for changes that alter task membership, verifier behavior,
   published outcomes, or the benchmark schema.
2. Keep `solution/`, `tests/`, credentials, private endpoints, internal paths,
   and unpublished data out of agent-visible inputs and logs.
3. Preserve the source repository, license, and task provenance fields for any
   benchmark-data change.
4. Run:

   ```bash
   python3 repro/audit_release_compliance.py
   python3 repro/validate_release.py
   ```

   The full release validator requires the benchmark downloaded under
   `dataset/tasks/`.

## Contributor License Agreement

Most contributions require you to agree to a Contributor License Agreement
(CLA) declaring that you have the right to, and actually do, grant us the
rights to use your contribution. For details, visit
https://cla.opensource.microsoft.com.

When you submit a pull request, a CLA bot will automatically determine whether
you need to provide a CLA and decorate the pull request appropriately. Follow
the instructions provided by the bot. You only need to do this once across all
repositories using our CLA.

## Pull request expectations

- Add the Microsoft copyright and MIT license header to new source files.
- Keep generated result changes separate from implementation changes.
- Explain any third-party code, data, model, or service introduced by the
  change and update `THIRD_PARTY_NOTICES.md` when applicable.
- Do not include secrets, personal data, proprietary software, internal tools,
  proprietary fonts, or unapproved product icons.
- Add or update focused validation for behavioral changes.

This project has adopted the
[Microsoft Open Source Code of Conduct](CODE_OF_CONDUCT.md).
