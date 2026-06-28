"""Shared constants, prompt builder, trial readers, robust ANNOTATION loader, and
agreement math for the trajectory-annotation study.

Static, dependency-free (stdlib only). Imported by run_annotation.py and agreement.py.

The annotation schema and rubric are defined authoritatively by the protocol markdown
(see PROTOCOL_REL below); this module loads that text into the agent prompt so the script
and the protocol never drift.
"""
from __future__ import annotations

import json
import math
import re
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]

# The self-contained annotation protocol fed to each labelling agent.
PROTOCOL_REL = (
    "conversations/260627-data-leakage-analysis/"
    "271117-claude-drafted-annotation-protocol.md"
)

# ---- Headline label spaces (one κ target per dimension) ---------------------
# Ordinal — weighted κ.
LEAKAGE_LABELS = ["none", "suspect", "confirmed"]
# Nominal.
EVIDENCE_MODES = ["evidence-first", "reactive-test-driven", "none"]
ALIGNMENT_LABELS = [
    "oracle-equivalent",
    "oracle-aligned-minor",
    "plausible-different",
    "suspicious-pass",
]
FAILURE_CATEGORIES = [
    "incomplete-migration",
    "wrong-semantic-output",
    "compile-namespace-inconsistency",
    "fixture-generated-state-inconsistent",
    "wrong-root-cause",
    "no-upgrade-attempted",
    "install-build-failure",
    "test-tampering",
    "gave-up-or-budget",
    "infra-exception",
]
CONFIDENCES = ["low", "med", "high"]

OUTPUT_FILENAME = "annotation.json"


# ---- Prompt -----------------------------------------------------------------

def load_protocol_text(protocol_path: Path | None = None) -> str:
    path = protocol_path or (REPO_ROOT / PROTOCOL_REL)
    return path.read_text(encoding="utf-8", errors="replace")


_PROMPT_PREAMBLE = r"""You are a post-hoc labelling agent. You are annotating ONE coding-agent
trial from a dependency-upgrade-repair benchmark. Do STATIC analysis only: DO NOT run, build,
compile, install, or execute anything; DO NOT modify any file except the single
`{output}` you will write at the end.

Your current working directory contains the trial's input bundle:
- `instruction.md`   : the task description the coding agent saw
- `oracle.patch`     : the gold source repair (`solution/code.patch`) — your "correct fix" reference
- `trajectory.json`  : the coding agent's full run trajectory — YOUR ONLY WINDOW INTO THE RUN
- `meta.json`        : {{trial, task, harness, llm, model, reward, exception_type}} — `reward` is authoritative
- `verifier_log.txt` : OPTIONAL — the held-out test run's stdout, present ONLY for some trials.
                       When present, use it to pin how a failing trial missed the hidden tests
                       (and to confirm a pass). When ABSENT, this file does not exist.

You do NOT have the held-out test *patch*. When `verifier_log.txt` is present, use it to
diagnose hidden-test failures directly; when it is absent, diagnose them by comparing the
agent's edits (from `trajectory.json`) to `oracle.patch`.

Follow the protocol below EXACTLY. Produce one JSON object per its §7 schema and WRITE it to a
file named exactly `{output}` in the current working directory (valid JSON, nothing else).
Set `annotator` to your own model id. After writing the file, print on the last line:
ANNOTATION_WRITTEN

==================== ANNOTATION PROTOCOL ====================

"""


def build_prompt(protocol_text: str) -> str:
    return _PROMPT_PREAMBLE.format(output=OUTPUT_FILENAME) + protocol_text


# ---- Trial discovery / meta -------------------------------------------------

def task_name_from_trial(trial_name: str) -> str:
    """`29ki__29k__3418__xGQXc6E` -> `29ki__29k__3418` (strip the trailing trial suffix)."""
    return trial_name.rsplit("__", 1)[0]


def _dig(obj: Any, *keys: str) -> Any:
    for k in keys:
        if not isinstance(obj, dict):
            return None
        obj = obj.get(k)
    return obj


def read_trial_meta(trial_dir: Path) -> dict[str, Any]:
    """Read result.json -> {trial, task, task_dir, harness, model, reward, exception_type,
    has_trajectory, trajectory_path}. Tolerant of missing fields."""
    trial_name = trial_dir.name
    traj_path = trial_dir / "agent" / "trajectory.json"
    meta: dict[str, Any] = {
        "trial": trial_name,
        "task": task_name_from_trial(trial_name),
        "task_dir": None,
        "harness": None,
        "model": None,
        "reward": None,
        "exception_type": None,
        "has_trajectory": traj_path.exists(),
        "trajectory_path": str(traj_path),
    }
    result_path = trial_dir / "result.json"
    if not result_path.exists():
        return meta
    try:
        r = json.loads(result_path.read_text(errors="replace"))
    except (json.JSONDecodeError, OSError):
        return meta
    task_path = _dig(r, "task_id", "path")
    if isinstance(task_path, str):
        meta["task_dir"] = task_path
        meta["task"] = Path(task_path).name
    meta["harness"] = _dig(r, "config", "agent", "name") or meta["harness"]
    meta["model"] = _dig(r, "config", "agent", "model_name") or meta["model"]
    reward = _dig(r, "verifier_result", "rewards", "reward")
    meta["reward"] = reward
    exc = _dig(r, "exception_info", "exception_type")
    meta["exception_type"] = exc
    return meta


# ---- ANNOTATION.json loading (robust) ---------------------------------------

_JSON_OBJ = re.compile(r"\{.*\}", re.DOTALL)


def _try_json_file(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        obj = json.loads(path.read_text(errors="replace"))
        return obj if isinstance(obj, dict) and "leakage" in obj else None
    except (json.JSONDecodeError, OSError):
        return None


def _scan_text_for_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    text = path.read_text(errors="replace")
    candidates: list[str] = []
    for m in re.finditer(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL):
        candidates.append(m.group(1))
    candidates.extend(m.group(0) for m in _JSON_OBJ.finditer(text))
    for chunk in reversed(candidates):
        try:
            obj = json.loads(chunk)
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict) and "leakage" in obj:
            return obj
    return None


def coerce_annotation(raw: dict[str, Any], meta: dict[str, Any]) -> dict[str, Any]:
    """Flatten the four headline labels + key sub-fields into a scoring record.

    The full agent object is preserved under `raw`; `reward` always comes from `meta`
    (authoritative), never from the agent.
    """
    lk = raw.get("leakage") or {}
    dc = raw.get("discovery") or {}
    pa = raw.get("pass_alignment") or {}
    fa = raw.get("failure") or {}
    if not isinstance(lk, dict):
        lk = {}
    if not isinstance(dc, dict):
        dc = {}
    if not isinstance(pa, dict):
        pa = {}
    if not isinstance(fa, dict):
        fa = {}

    def s(v: Any) -> str:
        return str(v).strip() if v is not None else ""

    return {
        "trial": meta["trial"],
        "task": meta["task"],
        "harness": meta.get("harness"),
        "model": meta.get("model"),
        "reward": meta.get("reward"),
        "annotator": s(raw.get("annotator")),
        "analyzable": raw.get("analyzable"),
        # headline labels
        "leakage_label": s(lk.get("label")),
        "evidence_gathering_mode": s(dc.get("evidence_gathering_mode")),
        "alignment_label": s(pa.get("alignment_label")),
        "failure_category_primary": s(fa.get("failure_category_primary")),
        # supporting fields
        "accessed_own_project": lk.get("accessed_own_project"),
        "retrieved_oracle": lk.get("retrieved_oracle"),
        "leakage_confidence": s(lk.get("confidence")),
        "docs_lookup": s(dc.get("docs_lookup")),
        "visible_then_hidden_overfit": dc.get("visible_then_hidden_overfit"),
        "key_change_matches": pa.get("key_change_matches"),
        "distance_to_oracle": s(fa.get("distance_to_oracle")),
    }


def empty_record(meta: dict[str, Any], parse_status: str = "missing") -> dict[str, Any]:
    rec = coerce_annotation({}, meta)
    rec["parse_status"] = parse_status
    rec["source_path"] = ""
    rec["raw"] = {}
    return rec


def load_annotation(
    *,
    meta: dict[str, Any],
    job_out_path: Path,
    trial_dir: Path,
    stage_dir: Path,
    agent_output_name: str,
) -> dict[str, Any]:
    """Return a scoring record with parse_status.

    parse_status: "ok" (clean annotation.json) | "json_repaired" (recovered from log/traj)
    | "missing". Search order: the copy written into the job dir, the harbor_lite artifact,
    the staged workspace, then the raw agent log / trajectory.
    """
    for path in (
        job_out_path,
        trial_dir / "artifacts" / OUTPUT_FILENAME,
        stage_dir / OUTPUT_FILENAME,
    ):
        obj = _try_json_file(path)
        if obj is not None:
            rec = coerce_annotation(obj, meta)
            rec["parse_status"] = "ok"
            rec["source_path"] = str(path)
            rec["raw"] = obj
            return rec
    for path in (
        trial_dir / "agent" / "trajectory.json",
        trial_dir / "artifacts" / agent_output_name,
        trial_dir / "agent" / agent_output_name,
    ):
        obj = _scan_text_for_json(path)
        if obj is not None:
            rec = coerce_annotation(obj, meta)
            rec["parse_status"] = "json_repaired"
            rec["source_path"] = str(path)
            rec["raw"] = obj
            return rec
    return empty_record(meta, "missing")


# ---- Agreement math (pure python) -------------------------------------------

def _counts(labels: list[str], universe: list[str]) -> dict[str, int]:
    c = {l: 0 for l in universe}
    for l in labels:
        c[l] = c.get(l, 0) + 1
    return c


def percent_and_kappa(pairs: list[tuple[str, str]]) -> dict[str, float | int]:
    """Cohen's κ (+ percent agreement). Only pairs with both labels non-empty are scored."""
    scored = [(a, b) for a, b in pairs if a and b]
    n = len(scored)
    if n == 0:
        return {"n": 0, "percent_agreement": float("nan"), "kappa": float("nan")}
    labels = sorted({l for pair in scored for l in pair})
    po = sum(1 for a, b in scored if a == b) / n
    ca = _counts([a for a, _ in scored], labels)
    cb = _counts([b for _, b in scored], labels)
    pe = sum((ca[l] / n) * (cb[l] / n) for l in labels)
    kappa = float("nan") if pe == 1.0 else (po - pe) / (1.0 - pe)
    return {"n": n, "percent_agreement": po, "kappa": kappa, "pe": pe}


def weighted_kappa(pairs: list[tuple[str, str]], order: list[str]) -> float:
    """Quadratic weighted κ for an ordered label set (e.g. none<suspect<confirmed)."""
    idx = {l: i for i, l in enumerate(order)}
    scored = [(a, b) for a, b in pairs if a in idx and b in idx]
    n = len(scored)
    if n == 0:
        return float("nan")
    k = len(order)
    if k < 2:
        return float("nan")
    w = [[((i - j) / (k - 1)) ** 2 for j in range(k)] for i in range(k)]
    ca = _counts([a for a, _ in scored], order)
    cb = _counts([b for _, b in scored], order)
    obs = [[0.0] * k for _ in range(k)]
    for a, b in scored:
        obs[idx[a]][idx[b]] += 1
    num = den = 0.0
    for i in range(k):
        for j in range(k):
            exp = ca[order[i]] * cb[order[j]] / n
            num += w[i][j] * obs[i][j]
            den += w[i][j] * exp
    return float("nan") if den == 0 else 1.0 - num / den


def gwet_ac1(pairs: list[tuple[str, str]]) -> float:
    """Gwet's AC1 — prevalence-robust agreement (better than κ for rare labels)."""
    scored = [(a, b) for a, b in pairs if a and b]
    n = len(scored)
    if n == 0:
        return float("nan")
    labels = sorted({l for pair in scored for l in pair})
    q = len(labels)
    if q < 2:
        return 1.0
    po = sum(1 for a, b in scored if a == b) / n
    pi = {l: (_counts([a for a, _ in scored], labels)[l] + _counts([b for _, b in scored], labels)[l]) / (2 * n) for l in labels}
    pe = sum(p * (1 - p) for p in pi.values()) / (q - 1)
    return float("nan") if pe == 1.0 else (po - pe) / (1.0 - pe)


def pabak(pairs: list[tuple[str, str]], n_categories: int) -> float:
    """Prevalence-and-bias-adjusted κ, generalized to q categories: (q·po − 1)/(q − 1)."""
    scored = [(a, b) for a, b in pairs if a and b]
    n = len(scored)
    if n == 0 or n_categories < 2:
        return float("nan")
    po = sum(1 for a, b in scored if a == b) / n
    return (n_categories * po - 1) / (n_categories - 1)


def confusion_matrix(pairs: list[tuple[str, str]], labels: list[str]) -> dict[str, dict[str, int]]:
    extra = sorted({l for pair in pairs for l in pair if l and l not in labels})
    row_labels = labels + extra
    matrix = {ra: {rb: 0 for rb in row_labels} for ra in row_labels}
    for a, b in pairs:
        if a and b and a in matrix and b in matrix[a]:
            matrix[a][b] += 1
    return matrix
