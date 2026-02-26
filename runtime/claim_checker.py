# MIT License © 2025 Motohiro Suzuki
from __future__ import annotations

from pathlib import Path
from typing import Any


def _load_yaml(path: Path) -> Any:
    try:
        import yaml  # type: ignore
    except Exception as e:
        raise RuntimeError(
            "PyYAML is required to parse Stage191 claims.yaml. "
            "Install with: python3 -m pip install pyyaml"
        ) from e
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _collect_claim_nodes(obj: Any) -> dict[str, dict[str, Any]]:
    if isinstance(obj, dict):
        if any(isinstance(k, str) and k.startswith("A") and k[1:].isdigit() for k in obj.keys()):
            return {
                k: v
                for k, v in obj.items()
                if isinstance(k, str) and k.startswith("A") and k[1:].isdigit() and isinstance(v, dict)
            }

        if "claims" in obj and isinstance(obj["claims"], dict):
            inner = obj["claims"]
            if any(isinstance(k, str) and k.startswith("A") and k[1:].isdigit() for k in inner.keys()):
                return {
                    k: v
                    for k, v in inner.items()
                    if isinstance(k, str) and k.startswith("A") and k[1:].isdigit() and isinstance(v, dict)
                }

        out: dict[str, dict[str, Any]] = {}
        for v in obj.values():
            sub = _collect_claim_nodes(v)
            out.update(sub)
        return out

    if isinstance(obj, list):
        out: dict[str, dict[str, Any]] = {}
        for v in obj:
            sub = _collect_claim_nodes(v)
            out.update(sub)
        return out

    return {}


def _normalize_jobs(val: Any) -> list[str]:
    if val is None:
        return []
    if isinstance(val, list):
        return [str(x) for x in val if str(x).strip()]
    if isinstance(val, str):
        s = val.strip()
        if not s:
            return []
        # comma-separated
        if "," in s:
            return [x.strip() for x in s.split(",") if x.strip()]
        return [s]
    # fallback
    return [str(val)]


def _extract_required_jobs(spec: dict[str, Any]) -> list[str]:
    # 優先順位で候補キーを探す
    candidates = [
        "required_jobs",
        "required_ci_jobs",
        "jobs",
        "ci_jobs",
        "required",
        "requires",
    ]
    for k in candidates:
        if k in spec:
            return _normalize_jobs(spec.get(k))

    # それでも無ければ、キー名に "job" を含むものを探索（最後の保険）
    for k, v in spec.items():
        if isinstance(k, str) and "job" in k.lower():
            jobs = _normalize_jobs(v)
            if jobs:
                return jobs
    return []


def evaluate_claims(claims_yaml: Path, jobs: list[dict[str, Any]]) -> dict[str, Any]:
    root = _load_yaml(claims_yaml)
    claims = _collect_claim_nodes(root)

    ok = set()
    for j in jobs:
        name = j.get("name")
        concl = j.get("conclusion")
        if name and concl == "success":
            ok.add(name)

    results: dict[str, Any] = {"claims_total": 0, "claims_passed": 0, "items": {}}

    for claim_id, spec in sorted(claims.items()):
        req = _extract_required_jobs(spec)

        missing = [r for r in req if r not in ok]
        passed = len(missing) == 0

        results["claims_total"] += 1
        if passed:
            results["claims_passed"] += 1

        results["items"][claim_id] = {
            "required_jobs": req,
            "missing_jobs": missing,
            "passed": passed,
            "spec_keys": sorted(list(spec.keys())),
        }

    results["all_passed"] = results["claims_total"] == results["claims_passed"]
    results["note"] = "Parsed via PyYAML; required_jobs extracted via candidate keys"
    return results
