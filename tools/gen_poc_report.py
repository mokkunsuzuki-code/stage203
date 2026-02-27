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

def main():
    runs = load_json(RUNS)
    jobs_payload = load_json(JOBS)
    claims = yaml.safe_load(CLAIMS.read_text(encoding="utf-8"))

    repo = runs.get("repo")
    chosen = runs.get("chosen", {}) if isinstance(runs.get("chosen"), dict) else {}
    run_id = chosen.get("id") or runs.get("run_id") or runs.get("id")
    run_url = chosen.get("html_url") or (f"https://github.com/{repo}/actions/runs/{run_id}" if repo and run_id else None)

    job_index = {j.get("name"): j for j in jobs_payload.get("jobs", []) if isinstance(j, dict) and j.get("name")}

    def find_job(required_name: str):
        if required_name in job_index:
            return job_index[required_name]
        # contains match for suffix/prefix variants
        for name, job in job_index.items():
            if name and (name.startswith(required_name) or required_name in name):
                return job
        return None

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
        if not isinstance(obj, dict):
            continue
        lines.append(f"### {claim}")
        rj = obj.get("required_jobs", []) or []
        ev = obj.get("evidence_paths", []) or []
        lines.append("- required_jobs:")
        for jn in rj:
            jn = str(jn)
            job = find_job(jn)
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
