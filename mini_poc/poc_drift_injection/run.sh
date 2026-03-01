#!/usr/bin/env bash
set -euo pipefail

mkdir -p out/evidence/attack_drift_injection
LOG="out/poc_logs/poc.jsonl"
OUT="out/evidence/attack_drift_injection/result.txt"

[[ -f "$LOG" ]] || { echo "[FAIL] missing $LOG" | tee "$OUT"; exit 1; }

python - << 'PY' "$LOG" "$OUT"
import json, sys
log_path, out_path = sys.argv[1], sys.argv[2]

# Until a dedicated CI job exists, we require the PoC to have reached claim_gate_passed.
required_event = "claim_gate_passed"
ok = False

with open(log_path, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        if obj.get("event") == required_event:
            ok = True

if ok:
    msg = f"[OK] verified event {required_event} present (evidence chain established)"
    code = 0
else:
    msg = f"[FAIL] missing event {required_event} in {log_path}"
    code = 1

with open(out_path, "w", encoding="utf-8") as w:
    w.write(msg + "\n")
print(msg)
raise SystemExit(code)
PY
