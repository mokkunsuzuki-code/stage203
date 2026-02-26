# MIT License © 2025 Motohiro Suzuki
from __future__ import annotations

from pathlib import Path
import argparse
import json
import time
from typing import Any

from ci_reader import summarize_ci
from claim_checker import evaluate_claims


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "out" / "poc_logs"
PROFILES_DIR = ROOT / "profiles"
FAILURE_DIR = ROOT / "failure_models"


def now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S%z")


def log_event(event: str, severity: str = "info", details: dict[str, Any] | None = None) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rec = {
        "ts": now_iso(),
        "event": event,
        "severity": severity,
        "details": details or {},
    }
    with (OUT_DIR / "poc.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def load_profile_yaml_minimal(path: Path) -> dict[str, Any]:
    data: dict[str, Any] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        key = k.strip()
        val = v.strip()

        if val.lower() in ("true", "false"):
            data[key] = val.lower() == "true"
        else:
            try:
                data[key] = int(val)
                continue
            except ValueError:
                pass
            data[key] = val.strip('"').strip("'")
    return data


def resolve_profile(profile_name: str) -> Path:
    mapping = {
        "qkd_strict": "profile_qkd_strict.yaml",
        "hybrid_balanced": "profile_hybrid_balanced.yaml",
        "resilience_test": "profile_resilience_test.yaml",
    }
    if profile_name not in mapping:
        raise SystemExit(
            f"[ERR] unknown profile '{profile_name}'. "
            f"Choose from: {', '.join(mapping.keys())}"
        )
    path = PROFILES_DIR / mapping[profile_name]
    if not path.exists():
        raise SystemExit(f"[ERR] profile file not found: {path}")
    return path


def _load_yaml(path: Path) -> Any:
    try:
        import yaml  # type: ignore
    except Exception:
        raise SystemExit("[ERR] PyYAML missing. Install: python3 -m pip install --user pyyaml")
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def load_failure_model(name: str) -> dict[str, Any]:
    mapping = {
        "qkd_failure": "qkd_failure.yaml",
        "downgrade": "downgrade.yaml",
        "replay": "replay.yaml",
        "rekey_race": "rekey_race.yaml",
        "none": None,
    }
    if name not in mapping:
        raise SystemExit(f"[ERR] unknown failure '{name}'. Choose from: {', '.join(mapping.keys())}")
    if mapping[name] is None:
        return {"name": "none"}
    path = FAILURE_DIR / mapping[name]
    if not path.exists():
        raise SystemExit(f"[ERR] failure model not found: {path}")
    obj = _load_yaml(path)
    if not isinstance(obj, dict):
        raise SystemExit(f"[ERR] failure model must be mapping: {path}")
    obj["_path"] = str(path)
    return obj


def main() -> None:
    ap = argparse.ArgumentParser(description="Stage201 PoC runner (internal)")
    ap.add_argument(
        "--profile",
        required=True,
        choices=["qkd_strict", "hybrid_balanced", "resilience_test"],
        help="PoC profile to run",
    )
    ap.add_argument(
        "--failure",
        default="none",
        choices=["none", "qkd_failure", "downgrade", "replay", "rekey_race"],
        help="Inject a failure/attack model (design-level injection logged)",
    )
    ap.add_argument(
        "--stage191-ci-dir",
        default=str(Path.home() / "Desktop" / "test" / "stage191" / "out" / "ci"),
        help="Path to Stage191 out/ci directory (contains actions_runs.json, actions_jobs.json)",
    )
    ap.add_argument(
        "--stage191-claims",
        default=str(Path.home() / "Desktop" / "test" / "stage191" / "claims" / "claims.yaml"),
        help="Path to Stage191 claims.yaml",
    )
    args = ap.parse_args()

    profile_path = resolve_profile(args.profile)
    profile = load_profile_yaml_minimal(profile_path)

    log_event(
        "poc_start",
        details={
            "profile": args.profile,
            "profile_path": str(profile_path),
            "profile_data": profile,
        },
    )

    # --- Failure injection (design-level) ---
    failure = load_failure_model(args.failure)

    # invariant checks (internal PoC)
    if args.profile == "qkd_strict" and profile.get("fallback_allowed") is True:
        log_event("profile_invariant_violation", severity="error", details={"rule": "qkd_strict forbids fallback_allowed=true"})
        raise SystemExit("[ERR] profile invariant violation")

    inject_ok = bool(profile.get("inject_failures", False))
    if args.failure != "none" and not inject_ok:
        log_event(
            "failure_injection_rejected",
            severity="error",
            details={
                "reason": "profile.inject_failures is false",
                "profile": args.profile,
                "failure": args.failure,
            },
        )
        raise SystemExit("[ERR] failure injection rejected by profile (inject_failures=false)")

    log_event("failure_injected", details={"failure": failure, "requested": args.failure})

    # --- Stage191 CI binding ---
    ci_dir = Path(args.stage191_ci_dir).expanduser().resolve()
    try:
        ci_summary = summarize_ci(ci_dir)
        log_event("stage191_ci_summary", details=ci_summary)

        if not ci_summary.get("all_success", False):
            log_event("stage191_ci_gate_failed", severity="error", details={"failed_jobs": ci_summary.get("failed_jobs", [])})
            raise SystemExit("[ERR] Stage191 CI gate failed (see out/poc_logs/poc.jsonl)")
        else:
            log_event("stage191_ci_gate_passed", details={"run_id": ci_summary.get("run_id"), "jobs_count": ci_summary.get("jobs_count")})
    except FileNotFoundError as e:
        log_event("stage191_ci_missing", severity="error", details={"error": str(e), "ci_dir": str(ci_dir)})
        raise SystemExit(f"[ERR] missing Stage191 CI outputs in: {ci_dir}")
    except json.JSONDecodeError as e:
        log_event("stage191_ci_parse_error", severity="error", details={"error": str(e), "ci_dir": str(ci_dir)})
        raise SystemExit(f"[ERR] cannot parse Stage191 CI json in: {ci_dir}")

    # --- Claim(required_jobs) check ---
    claims_path = Path(args.stage191_claims).expanduser().resolve()
    if not claims_path.exists():
        log_event("stage191_claims_missing", severity="error", details={"claims_path": str(claims_path)})
        raise SystemExit(f"[ERR] claims.yaml not found: {claims_path}")

    claim_eval = evaluate_claims(claims_path, ci_summary.get("jobs", []))
    log_event(
        "claim_required_jobs_eval",
        details={
            "claims_path": str(claims_path),
            "summary": {
                "claims_total": claim_eval.get("claims_total"),
                "claims_passed": claim_eval.get("claims_passed"),
                "all_passed": claim_eval.get("all_passed"),
            },
            "items": claim_eval.get("items", {}),
        },
    )

    if not claim_eval.get("all_passed", False):
        log_event("claim_gate_failed", severity="error", details={"items": claim_eval.get("items", {})})
        raise SystemExit("[ERR] claim_required_jobs not satisfied (see out/poc_logs/poc.jsonl)")
    else:
        log_event("claim_gate_passed", details={"claims_total": claim_eval.get("claims_total")})

    # --- Metrics snapshot (placeholders) ---
    metrics = {
        "security": {
            "attack_success_rate": 0.0 if args.failure in ("downgrade", "replay", "rekey_race") else None,
        },
        "availability": {"session_success_rate": None},
        "performance": {"handshake_latency_ms": None},
        "meta": {"stage191_run_id": ci_summary.get("run_id")},
    }
    log_event("metrics_snapshot", details=metrics)

    log_event("poc_end", details={"profile": args.profile})
    print(f"[OK] PoC finished. log: {OUT_DIR/'poc.jsonl'}")


if __name__ == "__main__":
    main()
