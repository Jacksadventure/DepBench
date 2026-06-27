"""Shared constants, audit prompt, robust VERDICT.json loader, and agreement math.

Static, dependency-free (stdlib only). Imported by run_audit.py and agreement.py.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

# ---- Label spaces -----------------------------------------------------------

VERDICTS = [
    "WITNESSES_BREAKING_CHANGE",
    "UNWITNESSED",
    "TESTS_OTHER_THING",
    "INCONCLUSIVE",
]

CATEGORIES = [
    "Direct Compatibility Witness",
    "Compatibility-Accommodation Test Update",
    "Toolchain/Static Check Oracle",
    "Drive-By Product Behavior Oracle",
    "Circular Implementation Oracle",
    "Test-Suite Maintenance Oracle",
    "Dead or Mis-Scoped Oracle",
    "No-Code-Pass / Latent Oracle",
    "Confounded Oracle",
]

DC_NATURES = [
    "REAL_SOURCE_REPAIR",
    "MIXED",
    "FORMATTER_LINT_CHURN",
    "CONFIG_INFRA_ONLY",
    "DOCS_EXAMPLE_ONLY",
    "TEST_ONLY",
    "SNAPSHOT_ONLY",
]

CONFIDENCES = ["low", "medium", "high"]


def is_witness(verdict: str) -> bool:
    return verdict == "WITNESSES_BREAKING_CHANGE"


# ---- Audit prompt -----------------------------------------------------------

AUDIT_PROMPT = r"""You are auditing ONE task from a dependency-upgrade "breaking change" benchmark.
Your current working directory IS the task directory. Do STATIC analysis only:
DO NOT run tests, build, compile, install, or execute anything. DO NOT modify any
file except the single VERDICT.json you will write at the end.

Read these files in the working directory:
- instruction.md            : the agent-facing task description
- task.toml                 : metadata (difficulty/solution notes, verifier command)
- solution/manifest.patch   : DELTA_M (Dm) — the dependency / manifest version bump
- solution/code.patch       : DELTA_C (Dc) — the human source repair for the upgrade
- tests/test.patch          : DELTA_T (Dt) — the HIDDEN test oracle being audited
- tests/test_state.py        : how Dt is applied at grading time
- tests/test.sh             : the actual verifier test command

Let P = the pre-upgrade project at the base commit. The locked Level-1 criterion for a
valid witnessed breaking change is BOTH of:
  (1) TEST(P + Dm + Dt) = FAIL   (with Dm but WITHOUT the source repair Dc, the hidden
      tests fail for a dependency-caused compile / type / runtime reason), AND
  (2) TEST(P + Dm + Dc + Dt) = PASS   (after the source repair Dc, they pass).
Lint/format/network/OOM/flaky failures do NOT count as a valid break.

Classify the task with this verdict (judge statically, predicting (1) and (2)):
- WITNESSES_BREAKING_CHANGE : Dt causally witnesses the dependency break; (1) and (2) hold.
- UNWITNESSED              : Dc is unnecessary/unreachable/erased/skipped/not run, or
                            P + Dm + Dt already passes (no-code-pass / latent / dead test).
- TESTS_OTHER_THING       : the fail/pass is not caused by the dependency break — e.g.
                            drive-by product behavior, pure lint/format/style, a circular
                            test that imports a symbol introduced only by Dc, or docs/
                            config/test-only Dc.
- INCONCLUSIVE            : a plausible witness exists but static review cannot establish
                            the causal fail/pass chain (vendoring, mixed facets, ambiguity).

Taxonomy category (pick the single best fit):
  Direct Compatibility Witness | Compatibility-Accommodation Test Update |
  Toolchain/Static Check Oracle | Drive-By Product Behavior Oracle |
  Circular Implementation Oracle | Test-Suite Maintenance Oracle |
  Dead or Mis-Scoped Oracle | No-Code-Pass / Latent Oracle | Confounded Oracle

Nature of Dc (solution/code.patch):
  REAL_SOURCE_REPAIR | MIXED | FORMATTER_LINT_CHURN | CONFIG_INFRA_ONLY |
  DOCS_EXAMPLE_ONLY | TEST_ONLY | SNAPSHOT_ONLY

Then WRITE a file named exactly VERDICT.json in the current working directory. It MUST be
valid JSON and nothing else, with EXACTLY these keys:

{
  "task": "<this task folder name>",
  "verdict": "WITNESSES_BREAKING_CHANGE | UNWITNESSED | TESTS_OTHER_THING | INCONCLUSIVE",
  "taxonomy_category": "<one of the categories above>",
  "delta_c_nature": "<one of the Dc natures above>",
  "import_only_delta_t": true,
  "dependency": {"library": "", "old_version": "", "new_version": ""},
  "predicted_precode_fail": true,
  "predicted_postcode_pass": true,
  "confidence": "low | medium | high",
  "key_risk_signals": ["..."],
  "rationale": "<= 150 words explaining the verdict"
}

"import_only_delta_t" = true if Dt only adapts import paths / package names / type shapes
(no new behavioral assertion). "predicted_precode_fail" and "predicted_postcode_pass" are
your static predictions of criteria (1) and (2). After writing VERDICT.json, print the
verdict on the last line as: VERDICT: <verdict>
"""


# ---- VERDICT.json loading ---------------------------------------------------

_JSON_OBJ = re.compile(r"\{.*\}", re.DOTALL)
_VERDICT_LINE = re.compile(r"VERDICT:\s*(" + "|".join(VERDICTS) + r")\b")


def _scan_verdict_line(path: Path) -> str | None:
    if not path.exists():
        return None
    matches = _VERDICT_LINE.findall(path.read_text(errors="replace"))
    return matches[-1] if matches else None


def _coerce(raw: dict[str, Any], task: str) -> dict[str, Any]:
    """Normalize a parsed object into the canonical record; unknown enums kept as-is."""
    dep = raw.get("dependency") or {}
    if not isinstance(dep, dict):
        dep = {}
    return {
        "task": raw.get("task") or task,
        "verdict": str(raw.get("verdict") or "").strip(),
        "taxonomy_category": str(raw.get("taxonomy_category") or "").strip(),
        "delta_c_nature": str(raw.get("delta_c_nature") or "").strip(),
        "import_only_delta_t": raw.get("import_only_delta_t"),
        "dependency": {
            "library": str(dep.get("library") or ""),
            "old_version": str(dep.get("old_version") or ""),
            "new_version": str(dep.get("new_version") or ""),
        },
        "predicted_precode_fail": raw.get("predicted_precode_fail"),
        "predicted_postcode_pass": raw.get("predicted_postcode_pass"),
        "confidence": str(raw.get("confidence") or "").strip(),
        "key_risk_signals": raw.get("key_risk_signals") or [],
        "rationale": str(raw.get("rationale") or "").strip(),
    }


def _try_json_file(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        obj = json.loads(path.read_text(errors="replace"))
        return obj if isinstance(obj, dict) and "verdict" in obj else None
    except (json.JSONDecodeError, OSError):
        return None


def _scan_text_for_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    text = path.read_text(errors="replace")
    # Prefer fenced json blocks, then the last brace-balanced object containing "verdict".
    candidates: list[str] = []
    for m in re.finditer(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL):
        candidates.append(m.group(1))
    candidates.extend(m.group(0) for m in _JSON_OBJ.finditer(text))
    for chunk in reversed(candidates):
        try:
            obj = json.loads(chunk)
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict) and "verdict" in obj:
            return obj
    return None


def load_verdict(
    *,
    task: str,
    trial_dir: Path,
    stage_dir: Path,
    agent_output_name: str,
) -> dict[str, Any]:
    """Return a record dict with a parse_status field.

    parse_status: "ok" (clean VERDICT.json) | "json_repaired" (recovered from log/traj)
    | "missing".
    """
    # 1) collected artifact, 2) staged dir copy
    for path in (trial_dir / "artifacts" / "VERDICT.json", stage_dir / "VERDICT.json"):
        obj = _try_json_file(path)
        if obj is not None:
            rec = _coerce(obj, task)
            rec["parse_status"] = "ok"
            rec["source_path"] = str(path)
            return rec
    # 3) recover from trajectory answer or raw agent log
    for path in (
        trial_dir / "agent" / "trajectory.json",
        trial_dir / "artifacts" / agent_output_name,
        trial_dir / "agent" / agent_output_name,
    ):
        obj = _scan_text_for_json(path)
        if obj is not None:
            rec = _coerce(obj, task)
            rec["parse_status"] = "json_repaired"
            rec["source_path"] = str(path)
            return rec
    # 4) last resort: a "VERDICT: <X>" line (agent reasoned but skipped the file).
    #    Only the verdict is recovered; descriptive fields stay empty (not kappa-scored).
    for path in (
        trial_dir / "artifacts" / agent_output_name,
        trial_dir / "agent" / agent_output_name,
        trial_dir / "agent" / "trajectory.json",
    ):
        v = _scan_verdict_line(path)
        if v is not None:
            rec = _coerce({"verdict": v, "task": task}, task)
            rec["parse_status"] = "verdict_line"
            rec["source_path"] = str(path)
            return rec
    return {
        "task": task,
        "verdict": "",
        "taxonomy_category": "",
        "delta_c_nature": "",
        "import_only_delta_t": None,
        "dependency": {"library": "", "old_version": "", "new_version": ""},
        "predicted_precode_fail": None,
        "predicted_postcode_pass": None,
        "confidence": "",
        "key_risk_signals": [],
        "rationale": "",
        "parse_status": "missing",
        "source_path": "",
    }


# ---- Agreement math (pure python) -------------------------------------------

def cohen_kappa(pairs: list[tuple[str, str]]) -> dict[str, float | int]:
    """Cohen's kappa for a list of (rater_a_label, rater_b_label) pairs.

    Only pairs where both labels are non-empty are scored.
    """
    scored = [(a, b) for a, b in pairs if a and b]
    n = len(scored)
    if n == 0:
        return {"n": 0, "percent_agreement": float("nan"), "kappa": float("nan")}
    labels = sorted({l for pair in scored for l in pair})
    agree = sum(1 for a, b in scored if a == b)
    po = agree / n
    count_a = {l: 0 for l in labels}
    count_b = {l: 0 for l in labels}
    for a, b in scored:
        count_a[a] += 1
        count_b[b] += 1
    pe = sum((count_a[l] / n) * (count_b[l] / n) for l in labels)
    kappa = float("nan") if pe == 1.0 else (po - pe) / (1.0 - pe)
    return {"n": n, "percent_agreement": po, "kappa": kappa, "pe": pe}


def confusion_matrix(pairs: list[tuple[str, str]], labels: list[str]) -> dict[str, dict[str, int]]:
    extra = sorted({l for pair in pairs for l in pair if l and l not in labels})
    row_labels = labels + extra
    matrix = {ra: {rb: 0 for rb in row_labels} for ra in row_labels}
    for a, b in pairs:
        if a and b and a in matrix and b in matrix[a]:
            matrix[a][b] += 1
    return matrix
