---
name: depupgrader
description: Repair dependency upgrades using version-matched migration evidence, affected-site searches, and minimal code changes.
---

# DepUpgrader

1. **Confirm the upgrade**: Apply or confirm the target version in the manifest and lockfile.
2. **Extract migration rules**: Read relevant, version-matched upstream docs or installed API/types. Record `old API -> new API | required edit | evidence`. Do not guess replacements.
3. **Find affected code**: Search imports, calls, and old symbols. Check aliases and local wrappers when needed.
4. **Make minimal edits**: Update affected imports, calls, types, and wrappers consistently. Adapt usage flow for behavior or lifecycle changes. Leave compatible code unchanged.
5. **Validate**: Confirm the resolved version, run focused build/type/test checks after the final edit, search for remaining old usages, and inspect the diff.
