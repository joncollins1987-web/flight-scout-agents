from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.db.repositories import get_final_result, get_run, list_runs


router = APIRouter(prefix="/api", tags=["runs"])


@router.get("/runs")
def get_runs(limit: int = 20) -> list[dict]:
    return list_runs(limit=limit)


@router.get("/runs/{run_id}")
def get_run_artifacts(run_id: str) -> dict:
    run = get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="run not found")

    final = get_final_result(run_id)
    return {
        "run": {
            "run_id": run.run_id,
            "timestamp": run.timestamp,
            "request_hash": run.request_hash,
            "status": run.status,
        },
        "final_result": final,
    }
