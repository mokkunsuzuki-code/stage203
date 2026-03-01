#!/usr/bin/env bash
set -euo pipefail

# MIT License © 2025 Motohiro Suzuki

log()  { printf "\n[INFO] %s\n" "$*"; }
warn() { printf "\n[WARN] %s\n" "$*" >&2; }
die()  { printf "\n[ERROR] %s\n" "$*" >&2; exit 1; }

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

PROFILE_DEFAULT="hybrid_balanced"
PROFILE="${PROFILE:-$PROFILE_DEFAULT}"
FAILURE="${FAILURE:-none}"

# If set to 1, run pip install. Default 0 for speed and clean separation.
INSTALL_DEPS="${INSTALL_DEPS:-0}"

log "QSP Stage203 – External-Ready PoC"
log "root: $ROOT"
log "profile: $PROFILE"
log "failure: $FAILURE"
log "install_deps: $INSTALL_DEPS"

have() { command -v "$1" >/dev/null 2>&1; }

have python || die "python not found. Install Python 3 and ensure it is on PATH."

if [[ "$INSTALL_DEPS" == "1" ]]; then
  if [[ -f "requirements.txt" ]]; then
    log "Install dependencies: requirements.txt"
    python -m pip install -r requirements.txt
  else
    die "requirements.txt not found"
  fi
  if [[ -f "requirements-dev.txt" ]]; then
    log "Install dev dependencies: requirements-dev.txt"
    python -m pip install -r requirements-dev.txt
  fi
else
  warn "Skipping pip install. (Set INSTALL_DEPS=1 to install requirements.)"
fi

log "Step 1/4: Run PoC main (fixed entrypoint + fixed profile)"
[[ -f "runtime/poc_runner.py" ]] || die "missing: runtime/poc_runner.py"
python runtime/poc_runner.py --profile "$PROFILE" --failure "$FAILURE"

log "Step 2/4: Run mini_poc suite (replay / downgrade / drift_injection)"

run_mini() {
  local name="$1"
  local script="mini_poc/${name}/run.sh"
  [[ -f "$script" ]] || die "missing: $script"
  log "run: $script"
  bash "$script"
}

run_mini "poc_replay"
run_mini "poc_downgrade"
run_mini "poc_drift_injection"

log "Step 3/4: Run tests (optional; skip if tests/ missing)"
if [[ -d "tests" ]]; then
  if have pytest; then
    pytest -q
  else
    if python -m pytest -q >/dev/null 2>&1; then
      python -m pytest -q
    else
      die "tests/ exists but pytest not available. Install: python -m pip install -r requirements-dev.txt"
    fi
  fi
else
  warn "tests/ not found (skip)."
fi

log "Step 4/4: Generate PoC report (fixed generator)"
if [[ -f "tools/generate_poc_report.py" ]]; then
  python tools/generate_poc_report.py
elif [[ -f "tools/gen_poc_report.py" ]]; then
  python tools/gen_poc_report.py
else
  die "missing report generator: tools/generate_poc_report.py (or tools/gen_poc_report.py)"
fi

log "Artifacts"
[[ -f "out/reports/poc_report.md" ]] && log "report: out/reports/poc_report.md" || warn "report not found at out/reports/poc_report.md"
[[ -f "out/poc_logs/poc.jsonl" ]] && log "log: out/poc_logs/poc.jsonl" || warn "log not found at out/poc_logs/poc.jsonl"

log "DONE ✅"
log "How to override"
echo "  INSTALL_DEPS=1 ./run_poc.sh"
echo "  PROFILE=qkd_strict INSTALL_DEPS=1 ./run_poc.sh"
echo "  PROFILE=resilience_test ./run_poc.sh"
echo "  FAILURE=downgrade ./run_poc.sh"
