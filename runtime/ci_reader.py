# MIT License © 2025 Motohiro Suzuki
from __future__ import annotations

from pathlib import Path
import json
from typing import Any


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _pick_first(d: dict[str, Any], keys: list[str]) -> Any:
    for k in keys:
        if k in d and d[k] is not None:
            return d[k]
    return None


def summarize_ci(ci_dir: Path) -> dict[str, Any]:
    """
    Stage191 が出力する out/ci/actions_runs.json / actions_jobs.json の最小サマリを返す。
    run_id は actions_runs.json と actions_jobs.json の両方から“確実に”拾う。
    """
    runs_path = ci_dir / "actions_runs.json"
    jobs_path = ci_dir / "actions_jobs.json"
    if not runs_path.exists():
        raise FileNotFoundError(f"missing: {runs_path}")
    if not jobs_path.exists():
        raise FileNotFoundError(f"missing: {jobs_path}")

    runs = read_json(runs_path)
    jobs = read_json(jobs_path)

    repo = runs.get("repo", "unknown")

    # --- run_id をできるだけ広く拾う（Stage191の出力差分吸収） ---
    # actions_runs.json 側
    run_id_runs = _pick_first(
        runs,
        [
            "run_id",
            "chosen_run_id",
            "id",
            "runId",
            "runID",
        ],
    )

    # actions_runs.json が list を内包してる場合も吸収（例: runs["runs"][0]["id"] 等）
    if run_id_runs is None:
        for k in ("runs", "items", "data"):
            if isinstance(runs.get(k), list) and runs[k]:
                if isinstance(runs[k][0], dict):
                    run_id_runs = _pick_first(runs[k][0], ["id", "run_id", "runId"])
                    if run_id_runs is not None:
                        break

    # actions_jobs.json 側（あなたのログではこっちが取れている）
    run_id_jobs = _pick_first(
        jobs,
        [
            "run_id",
            "id",
        ],
    )
    if run_id_jobs is None:
        raw = jobs.get("raw")
        if isinstance(raw, dict):
            run_id_jobs = _pick_first(raw, ["id", "run_id", "runId"])

    # 優先順位：runs側があればそれ、なければjobs側
    run_id = run_id_runs if run_id_runs is not None else run_id_jobs
    run_id_str = str(run_id) if run_id is not None else "unknown"

    jobs_list = jobs.get("jobs", [])
    simple_jobs = []
    for j in jobs_list:
        simple_jobs.append(
            {
                "name": j.get("name"),
                "status": j.get("status"),
                "conclusion": j.get("conclusion"),
            }
        )

    failed = [j for j in simple_jobs if j.get("conclusion") not in (None, "success")]
    all_success = len(failed) == 0

    return {
        "repo": repo,
        "run_id": run_id_str,
        "run_id_sources": {"runs": run_id_runs, "jobs": run_id_jobs},
        "jobs_count": len(simple_jobs),
        "all_success": all_success,
        "failed_jobs": failed,
        "jobs": simple_jobs,
        "paths": {
            "runs": str(runs_path),
            "jobs": str(jobs_path),
        },
    }
