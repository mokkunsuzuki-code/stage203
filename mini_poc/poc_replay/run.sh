#!/usr/bin/env bash
set -euo pipefail

mkdir -p out/evidence/attack_replay
LOG="out/poc_logs/poc.jsonl"
OUT="out/evidence/attack_replay/result.txt"

[[ -f "$LOG" ]] || { echo "[FAIL] missing $LOG" | tee "$OUT"; exit 1; }

python - << 'PY' "$LOG" "$OUT"
import json, sys
log_path, out_path = sys.argv[1], sys.argv[2]

want_job = "attack_replay"
found_summary = False
ok = False
last_run_id = None

with open(log_path, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        if obj.get("event") == "stage191_ci_summary":
            found_summary = True
            det = obj.get("details", {}) or {}
            last_run_id = det.get("run_id")
            for j in det.get("jobs", []) or []:
                if j.get("name") == want_job:
                    ok = (j.get("conclusion") == "success")
            # keep scanning; but later summaries would overwrite ok/run_id

msg = ""
code = 1
if not found_summary:
    msg = f"[FAIL] no stage191_ci_summary in {log_path}"
elif not ok:
    msg = f"[FAIL] stage191 job {want_job} not success (run_id={last_run_id})"
else:
    msg = f"[OK] verified stage191 job {want_job}=success (run_id={last_run_id})"
    code = 0

with open(out_path, "w", encoding="utf-8") as w:
    w.write(msg + "\n")
print(msg)
raise SystemExit(code)
PY
