# Stage202 Mini-PoC Report

## GitHub Actions Run
- Run URL: https://github.com/mokkunsuzuki-code/stage202/actions/runs/22536674004
- Run ID: `22536674004`

## Claims → Required CI Jobs → Evidence

| Claim | Required job | Result | Job link | Evidence path |
|---|---|---|---|---|
| A2 | `attack_replay` | **success** | https://github.com/mokkunsuzuki-code/stage202/actions/runs/22536674004/job/65285393403 | `out/evidence/attack_replay/result.txt` |
| A3 | `attack_downgrade` | **success** | https://github.com/mokkunsuzuki-code/stage202/actions/runs/22536674004/job/65285393397 | `out/evidence/attack_downgrade/result.txt` |
| A4 | `attack_drift_injection` | **success** | https://github.com/mokkunsuzuki-code/stage202/actions/runs/22536674004/job/65285393388 | `out/evidence/attack_drift_injection/result.txt` |
| A5 | `interop_smoke` | **success** | https://github.com/mokkunsuzuki-code/stage202/actions/runs/22536674004/job/65285393400 | `out/evidence/interop_smoke/smoke.txt` |

## Evidence Bundle (artifact)
- Included paths:
  - `poc_report.md`
  - `claims/claims.yaml`
  - `out/ci/actions_runs.json`
  - `out/ci/actions_jobs.json`
  - `out/evidence/**`
