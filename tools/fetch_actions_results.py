# MIT License © 2025 Motohiro Suzuki
from __future__ import annotations

import argparse
import json
import os
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional


def sh(cmd: List[str], env: Optional[Dict[str, str]] = None) -> str:
    r = subprocess.run(cmd, check=True, text=True, capture_output=True, env=env)
    return r.stdout


def gh_env() -> Dict[str, str]:
    env = os.environ.copy()
    # GitHub Actions: GH_TOKEN or GITHUB_TOKEN
    # Local: you likely already did `gh auth login`
    if "GH_TOKEN" not in env and "GITHUB_TOKEN" in env:
        env["GH_TOKEN"] = env["GITHUB_TOKEN"]
    return env


def load_json(s: str) -> Any:
    return json.loads(s) if s.strip() else None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True, help="owner/repo")
    ap.add_argument("--run-id", type=int, default=None, help="Fix the target run_id (fail-closed).")
    ap.add_argument("--out-dir", default="out/ci", help="Output directory")
    args = ap.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    env = gh_env()

    # 1) Determine run_id
    if args.run_id is not None:
        run_id = args.run_id
    else:
        # fallback: latest run
        runs_json = sh(
            [
                "gh",
                "run",
                "list",
                "--repo",
                args.repo,
                "--limit",
                "1",
                "--json",
                "databaseId,status,conclusion,createdAt,headSha,displayTitle,event",
            ],
            env=env,
        )
        runs = load_json(runs_json) or []
        if not runs:
            raise SystemExit("[ERR] no runs found")
        run_id = int(runs[0]["databaseId"])

    # 2) Fetch run (single) + jobs (for that run)
    run_json = sh(
        [
            "gh",
            "run",
            "view",
            str(run_id),
            "--repo",
            args.repo,
            "--json",
            "databaseId,status,conclusion,createdAt,headSha,displayTitle,event,htmlURL",
        ],
        env=env,
    )
    run_obj = load_json(run_json)

    jobs_json = sh(
        [
            "gh",
            "run",
            "view",
            str(run_id),
            "--repo",
            args.repo,
            "--json",
            "jobs",
        ],
        env=env,
    )
    jobs_obj = load_json(jobs_json)

    runs_out = out_dir / "actions_runs.json"
    jobs_out = out_dir / "actions_jobs.json"

    runs_out.write_text(
        json.dumps({"repo": args.repo, "run_id": run_id, "run": run_obj}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    jobs_out.write_text(
        json.dumps({"repo": args.repo, "run_id": run_id, "jobs": jobs_obj.get("jobs", [])}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"[OK] wrote: {runs_out}")
    print(f"[OK] wrote: {jobs_out}")
    print(f"[OK] chosen run: {run_id}")


if __name__ == "__main__":
    main()
