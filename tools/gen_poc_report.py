# MIT License © 2025 Motohiro Suzuki
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_yaml(path: Path) -> Any:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def job_index(jobs: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    # jobs items usually include: name, conclusion, status, startedAt, completedAt, url/html_url, databaseId etc.
    idx: Dict[str, Dict[str, Any]] = {}
    for j in jobs:
        name = j.get("name") or j.get("workflowName") or j.get("id")
        if name:
            idx[str(name)] = j
    return idx


def best_job_url(repo: str, run_id: int, job: Dict[str, Any]) -> str:
    # gh JSON fields differ by version; prefer htmlURL/url/html_url
    for k in ("htmlURL", "htmlUrl", "html_url", "url"):
        v = job.get(k)
        if isinstance(v, str) and v.startswith("http"):
            return v
    # fallback: linkable run page (job is still identifiable there)
    return f"https://github.com/{repo}/actions/runs/{run_id}"


def fmt_conclusion(job: Dict[str, Any]) -> str:
    c = job.get("conclusion") or job.get("conclusionStatus") or job.get("result")
    s = job.get("status")
    if c:
        return str(c)
    if s:
        return str(s)
    return "unknown"


def main() -> None:
    repo = Path("out/ci/actions_runs.json")
    jobs = Path("out/ci/actions_jobs.json")
    claims_p = Path("claims/claims.yaml")
    out_p = Path("poc_report.md")

    if not repo.exists() or not jobs.exists():
        raise SystemExit("[ERR] missing out/ci/actions_runs.json or actions_jobs.json. Run fetch_actions_results.py first.")
    if not claims_p.exists():
        raise SystemExit("[ERR] missing claims/claims.yaml")

    runs_obj = load_json(repo)
    jobs_obj = load_json(jobs)
    claims_obj = load_yaml(claims_p)

    repo_name = runs_obj.get("repo", "")
    run_id = int(runs_obj.get("run_id"))
    run_html = (runs_obj.get("run") or {}).get("htmlURL") or (runs_obj.get("run") or {}).get("htmlUrl") or (runs_obj.get("run") or {}).get("html_url")
    if not run_html:
        run_html = f"https://github.com/{repo_name}/actions/runs/{run_id}"

    jobs_list = jobs_obj.get("jobs", [])
    jidx = job_index(jobs_list)

    claims = (claims_obj or {}).get("claims", {})

    lines: List[str] = []
    lines.append("# Stage202 Mini-PoC Report")
    lines.append("")
    lines.append("## GitHub Actions Run")
    lines.append(f"- Run URL: {run_html}")
    lines.append(f"- Run ID: `{run_id}`")
    lines.append("")
    lines.append("## Claims → Required CI Jobs → Evidence")
    lines.append("")
    lines.append("| Claim | Required job | Result | Job link | Evidence path |")
    lines.append("|---|---|---|---|---|")

    for claim_id, meta in claims.items():
        req_jobs = meta.get("required_jobs", []) or []
        ev_paths = meta.get("evidence_paths", []) or []

        # fail-closed: require at least 1 job
        if not req_jobs:
            lines.append(f"| {claim_id} | **MISSING** | unknown | (none) | {', '.join(ev_paths) if ev_paths else '(none)'} |")
            continue

        for i, job_name in enumerate(req_jobs):
            job = jidx.get(job_name)
            if not job:
                # fail-closed: job not found in this run
                lines.append(f"| {claim_id if i==0 else ''} | `{job_name}` | **NOT FOUND IN RUN** | {run_html} | {ev_paths[i] if i < len(ev_paths) else ''} |")
                continue

            result = fmt_conclusion(job)
            link = best_job_url(repo_name, run_id, job)
            ev = ev_paths[i] if i < len(ev_paths) else ""
            lines.append(f"| {claim_id if i==0 else ''} | `{job_name}` | **{result}** | {link} | `{ev}` |")

    lines.append("")
    lines.append("## Evidence Bundle (artifact)")
    lines.append("- Included paths:")
    lines.append("  - `poc_report.md`")
    lines.append("  - `claims/claims.yaml`")
    lines.append("  - `out/ci/actions_runs.json`")
    lines.append("  - `out/ci/actions_jobs.json`")
    lines.append("  - `out/evidence/**`")
    lines.append("")

    out_p.write_text("\n".join(lines), encoding="utf-8")
    print("[OK] wrote poc_report.md")


if __name__ == "__main__":
    main()
