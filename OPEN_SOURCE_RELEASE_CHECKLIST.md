# Open Source Release Compliance Checklist

This checklist records repository preparation only. It does not assert that
Microsoft internal approvals have been granted.

## Completed in this repository

- [x] Root README describes purpose, state, artifacts, third-party content,
  network behavior, and telemetry.
- [x] Standard MIT license added for Microsoft-authored code, documentation,
  and brand assets.
- [x] Contribution guidance includes the Microsoft CLA process.
- [x] Microsoft security policy and private vulnerability reporting path added.
- [x] Microsoft Open Source Code of Conduct added.
- [x] Support expectations added.
- [x] Third-party repository and license inventory linked and exceptional
  licenses summarized.
- [x] Source files carry the Microsoft copyright and MIT license header.
- [x] Current source tree excludes known internal codenames and the option to
  serialize authentication environment values into generated configs.
- [x] Repeatable repository compliance audit added.

## Required owner actions before or as part of release

- [ ] Register the release in the Open Source Portal and complete business and
  OSSOM CELA review.
- [ ] Confirm the repository is hosted in an approved 1ES-managed GitHub
  organization and link approval to any pre-existing repository.
- [ ] Complete project naming review and obtain approval for the DepBench name
  and logo where required.
- [ ] Complete the Microsoft Open Data review for the Hugging Face dataset and
  retain the approval record.
- [ ] Obtain CELA disposition for the 11 tasks with source-available, custom, or
  undeclared terms, including `LicenseRef-Databricks`.
- [ ] Complete privacy review for benchmark prompts, source excerpts,
  contributor identifiers, and Hugging Face artifacts.
- [ ] Complete the applicable SDL/security review, threat model, secret scan,
  dependency review, and PoliCheck run.
- [ ] Produce and review the required software bill of materials or equivalent
  supply-chain inventory.
- [ ] Confirm any Microsoft or third-party trademark and product-icon use with
  Frontline CELA.
- [ ] Confirm staffing for issue triage, security response, dependency updates,
  pull request review, and future releases.

## AI and generative AI review

- [ ] Review the applicable Responsible AI Standard requirements with the
  division RAI Champ.
- [ ] Submit the OneRAI Responsible AI Deployment Safety Board intake because
  the project evaluates generative-AI coding agents.
- [ ] Confirm with CELA and the RAI Champ whether this benchmark release is
  classified as a dataset/research artifact only or also requires any model
  release documentation. DepBench does not publish model weights.

## Historical and artifact review

- [ ] Decide whether the existing Git history is eligible for publication. The
  current history contains Microsoft corporate email addresses and prior
  internal-codename references. Use the approved history-cleaning process or
  obtain an explicit review disposition before publishing that history.
- [ ] Review the full Git history, not only the current tree, for internal
  paths, aliases, email addresses, codenames, credentials, and confidential
  information before making a new repository public.
- [ ] Review known secret-scanner findings in upstream public test fixtures,
  including example private-key material, and document approved suppressions
  or remove affected artifacts without changing benchmark semantics. The
  current grouped findings are in
  `analysis/secret_scan_review_2026-07-23.csv`.
- [ ] Confirm that Docker task images and the Hugging Face snapshot correspond
  to the reviewed commit, immutable digests, and approved third-party terms.
