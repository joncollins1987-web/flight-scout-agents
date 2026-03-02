from __future__ import annotations

import json
from datetime import datetime

from sqlmodel import Session, col, select

from app.core.cache import is_fresh
from app.db.engine import engine
from app.db.models import CandidateRecord, FinalResultRecord, RunRecord, VerifiedRecord


def create_run(run_id: str, request_hash: str, request_json: str, status: str = "started") -> RunRecord:
    with Session(engine) as session:
        record = RunRecord(run_id=run_id, request_hash=request_hash, request_json=request_json, status=status)
        session.add(record)
        session.commit()
        session.refresh(record)
        return record


def update_run_status(run_id: str, status: str) -> None:
    with Session(engine) as session:
        record = session.get(RunRecord, run_id)
        if record:
            record.status = status
            session.add(record)
            session.commit()


def save_candidates(run_id: str, source: str, candidates: list[dict]) -> None:
    with Session(engine) as session:
        for candidate in candidates:
            session.add(CandidateRecord(run_id=run_id, source=source, candidate_json=json.dumps(candidate, default=str)))
        session.commit()


def save_verified(run_id: str, verified_json: dict, evidence_json: dict) -> None:
    with Session(engine) as session:
        session.add(
            VerifiedRecord(
                run_id=run_id,
                verified_json=json.dumps(verified_json, default=str),
                evidence_json=json.dumps(evidence_json, default=str),
            )
        )
        session.commit()


def save_final_result(run_id: str, final_json: dict) -> None:
    with Session(engine) as session:
        session.add(FinalResultRecord(run_id=run_id, final_json=json.dumps(final_json, default=str)))
        session.commit()


def get_run(run_id: str) -> RunRecord | None:
    with Session(engine) as session:
        return session.get(RunRecord, run_id)


def get_final_result(run_id: str) -> dict | None:
    with Session(engine) as session:
        statement = select(FinalResultRecord).where(FinalResultRecord.run_id == run_id).order_by(col(FinalResultRecord.id).desc())
        record = session.exec(statement).first()
        if not record:
            return None
        return json.loads(record.final_json)


def get_candidates_for_run(run_id: str) -> list[dict]:
    with Session(engine) as session:
        statement = select(CandidateRecord).where(CandidateRecord.run_id == run_id)
        rows = session.exec(statement).all()
        return [json.loads(r.candidate_json) for r in rows]


def get_latest_run_by_hash(
    request_hash: str,
    ttl_minutes: int,
    exclude_run_id: str | None = None,
) -> RunRecord | None:
    with Session(engine) as session:
        statement = select(RunRecord).where(RunRecord.request_hash == request_hash)
        if exclude_run_id:
            statement = statement.where(RunRecord.run_id != exclude_run_id)
        statement = statement.order_by(col(RunRecord.timestamp).desc())
        run = session.exec(statement).first()
        if not run:
            return None
        if not is_fresh(run.timestamp, ttl_minutes):
            return None
        return run


def get_latest_run_any_age(request_hash: str) -> RunRecord | None:
    with Session(engine) as session:
        statement = (
            select(RunRecord)
            .where(RunRecord.request_hash == request_hash)
            .order_by(col(RunRecord.timestamp).desc())
        )
        return session.exec(statement).first()


def get_verified_for_run(run_id: str) -> list[dict]:
    with Session(engine) as session:
        statement = select(VerifiedRecord).where(VerifiedRecord.run_id == run_id)
        rows = session.exec(statement).all()
        return [json.loads(r.verified_json) for r in rows]


def list_runs(limit: int = 50) -> list[dict]:
    with Session(engine) as session:
        statement = select(RunRecord).order_by(col(RunRecord.timestamp).desc()).limit(limit)
        rows = session.exec(statement).all()
        return [
            {
                "run_id": row.run_id,
                "timestamp": row.timestamp,
                "request_hash": row.request_hash,
                "status": row.status,
            }
            for row in rows
        ]
