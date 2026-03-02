from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Field, SQLModel


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class RunRecord(SQLModel, table=True):
    __tablename__ = "runs"

    run_id: str = Field(primary_key=True)
    timestamp: datetime = Field(default_factory=utcnow, nullable=False)
    request_hash: str = Field(index=True, nullable=False)
    request_json: str = Field(nullable=False)
    status: str = Field(default="started", nullable=False)


class CandidateRecord(SQLModel, table=True):
    __tablename__ = "candidates"

    id: Optional[int] = Field(default=None, primary_key=True)
    run_id: str = Field(index=True, nullable=False)
    source: str = Field(nullable=False)
    candidate_json: str = Field(nullable=False)


class VerifiedRecord(SQLModel, table=True):
    __tablename__ = "verified"

    id: Optional[int] = Field(default=None, primary_key=True)
    run_id: str = Field(index=True, nullable=False)
    verified_json: str = Field(nullable=False)
    evidence_json: str = Field(nullable=False)


class FinalResultRecord(SQLModel, table=True):
    __tablename__ = "final_results"

    id: Optional[int] = Field(default=None, primary_key=True)
    run_id: str = Field(index=True, nullable=False)
    final_json: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=utcnow, nullable=False)
