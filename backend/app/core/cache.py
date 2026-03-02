from __future__ import annotations

from datetime import datetime, timedelta, timezone


def is_fresh(created_at: datetime, ttl_minutes: int) -> bool:
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)
    return datetime.now(timezone.utc) - created_at < timedelta(minutes=ttl_minutes)


def expires_at(created_at: datetime, ttl_minutes: int) -> datetime:
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)
    return created_at + timedelta(minutes=ttl_minutes)
