Stage203 is open for external review and critique.

This stage establishes:

- Reproducible PoC execution (`./run_poc.sh`)
- Claim-bound CI verification
- Structured claim → job → artifact linkage
- Machine-readable evidence logs (`poc.jsonl`)

### Non-goals

- No unconditional QKD guarantees
- No formal proof completeness claim
- No production deployment claim

### Review Thread

We welcome architectural critique, assumption analysis, attack expansion suggestions, and CI verification feedback.

👉 Review here:  
https://github.com/mokkunsuzuki-code/stage203/issues/1

👉 Release:  
https://github.com/mokkunsuzuki-code/stage203/releases/tag/v0.3-stage203

---

QSP: Claim-Bound, CI-Verifiable Quantum-Safe Session Architecture  
MIT License © 2025 Motohiro Suzuki

---

## Overview

Stage203 upgrades Stage202 into an **external-review-ready PoC**.

This stage provides:

- One-command reproducibility
- Automatic evidence generation
- Claim ↔ CI job binding
- Machine-verifiable PoC report
- GitHub Actions artifact output

This is not a theoretical security claim.

This is a reproducible execution-bound structure.

---

## Quick Review (1 Command)

### 🔵 Full Evidence Chain (Local – Recommended)

```bash
INSTALL_DEPS=1 ./run_poc.sh

This generates:

out/poc_logs/poc.jsonl

out/evidence/**

out/reports/poc_report.md

This is the authoritative verification path.

🟢 CI (Artifact Generation)

GitHub Actions automatically:

Generates PoC evidence bundle

Fetches job results

Produces poc_report.md

Uploads stage203-poc-report artifact

Note:

CI uses a portable stub PoC log for environment independence.
Full external-chain validation is performed locally via:

./run_poc.sh
What Stage203 Guarantees

Stage203 enforces:

Claim transparency

Explicit evidence paths

Fail-closed semantics

CI-bound artifact generation

Machine-readable execution logs

Security claims cannot silently degrade.

Claims Structure

Defined in:

claims/claims.yaml

Each claim contains:

required_jobs

evidence_paths

Example:

claims:
  A2:
    required_jobs: ["attack_replay"]
    evidence_paths:
      - "out/evidence/attack_replay/result.txt"

Claims are mapped to execution artifacts.

Execution Flow
Step 1 — PoC Execution

runtime/poc_runner.py

Produces:

out/poc_logs/poc.jsonl
Step 2 — Attack Validation

mini_poc/poc_replay

mini_poc/poc_downgrade

mini_poc/poc_drift_injection

Each produces evidence under:

out/evidence/
Step 3 — Report Generation
tools/gen_poc_report.py

Produces:

out/reports/poc_report.md
Evidence Chain

The PoC log contains structured events:

{"event":"claim_gate_passed"}
{"event":"stage191_ci_summary", ...}

mini_poc scripts verify:

CI job success (if present)

Or fallback to claim_gate verification

CI-safe behavior in GitHub Actions

GitHub Actions Workflow

Workflow:

.github/workflows/stage203-ci.yml

Produces artifact:

stage203-poc-report

Includes:

poc_report.md

claims.yaml

actions_runs.json

actions_jobs.json

out/evidence/**

out/poc_logs/poc.jsonl

Retention: 90 days.

Repository Structure
stage203/
├── runtime/
├── mini_poc/
├── claims/
├── tools/
├── out/
├── .github/workflows/
├── run_poc.sh
├── requirements.txt
└── README.md
Non-Goals

Stage203 does NOT claim:

Unconditional QKD security

Formal proof completeness

Production deployment readiness

Network-level attack resistance

This stage establishes:

Reproducible claim → execution → evidence linkage.

Nothing more. Nothing hidden.

Review Guidance

If you are reviewing this project:

Run:

INSTALL_DEPS=1 ./run_poc.sh

Inspect:

out/reports/poc_report.md

out/evidence/**

Open a GitHub Issue using the provided review template.

Why Stage203 Matters

Before institutional collaboration or academic review, a system must prove:

Claims are structured

Claims are testable

Claims produce artifacts

Claims cannot silently regress

Stage203 satisfies that threshold.

License

MIT License © 2025 Motohiro Suzuki