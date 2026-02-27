# MIT License © 2025 Motohiro Suzuki
import json
from pathlib import Path
import yaml

ROOT = Path(".")
RUNS = ROOT / "out/ci/actions_runs.json"
JOBS = ROOT / "out/ci/actions_jobs.json"
CLAIMS = ROOT / "claims/claims.yaml"
OUT = ROOT / "poc_report.md"

def load_json(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))

def pick_run_info(runs: dict):
    repo = runs.get("repo")

    # try common locations
    run_id = runs.get("run_id") or runs.get("chosen_run_id") or runs.get("id")

    raw = runs.get("raw", {})
    run_url = None

    # Stage191 style: raw.chosen.html_url
    if isinstance(raw, dict):
        chosen = raw.get("chosen") or raw.get("run") or raw.get("workflow_run")
        if isinstance(chosen, dict):
            run_url = chosen.get("html_url") or chosen.get("url")
            run_id = run_id or chosen.get("id")

    # fallback build URL
    if repo and run_id and not run_url:
        run_url = f"https://github.com/{repo}/actions/runs/{run_id}"

    return repo, run_id, run_url

def build_job_index(jobs_payload: dict):
    jobs = jobs_payload.get("jobs", [])
    idx = {}
    for j in jobs:
        if isinstance(j, dict) and j.get("name"):
            idx[str(j["name"])] = j
    return idx

def find_job(required_name: str, job_index: dict):
    # 1) exact match
    if required_name in job_index:
        return job_index[required_name]

    # 2) prefix/contains match (job名に suffix が付くケースに対応)
    cand = []
    for name, job in job_index.items():
        if name == required_name:
            return job
        if name.startswith(required_name):
            cand.append((0, name, job))
        elif required_name in name:
            cand.append((1, name, job))
    if cand:
        cand.sort(key=lambda x: (x[0], len(x[1])))
        return cand[0][2]
    return None

def main():
    runs = load_json(RUNS)
    jobs_payload = load_json(JOBS)
    claims = yaml.safe_load(CLAIMS.read_text(encoding="utf-8"))

    repo, run_id, run_url = pick_run_info(runs)

    job_index = build_job_index(jobs_payload)

    lines = []
    lines.append("# PoC Report (Stage202)")
    lines.append("")
    lines.append(f"- Repo: `{repo}`")
    lines.append(f"- Run ID: `{run_id}`")
    lines.append(f"- Run URL: {run_url}")
    lines.append("")
    lines.append("## Claim → required_jobs → CI job link")
    lines.append("")

    claims_root = claims.get("claims", claims)
    for claim, obj in claims_root.items():
        lines.append(f"### {claim}")
        rj = obj.get("required_jobs", []) or []
        ev = obj.get("evidence_paths", []) or []
        lines.append("- required_jobs:")
        for jn in rj:
            jn = str(jn)
            job = find_job(jn, job_index)
            if job:
                name = job.get("name")
                url = job.get("html_url")
                concl = job.get("conclusion") or job.get("status")
                if url:
                    lines.append(f"  - [{name}]({url}) ({concl})")
                else:
                    lines.append(f"  - {name} ({concl})")
            else:
                lines.append(f"  - {jn} (not found)")
        lines.append("- evidence_paths:")
        for e in ev:
            lines.append(f"  - `{e}`")
        lines.append("")

    OUT.write_text("\n".join(lines), encoding="utf-8")
    print("[OK] wrote poc_report.md")

if __name__ == "__main__":
    main()
