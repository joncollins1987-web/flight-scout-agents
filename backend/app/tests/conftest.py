from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.core.config import settings
from app.db.engine import init_db


@pytest.fixture(scope="session", autouse=True)
def clean_test_db() -> None:
    prefix = "sqlite:///"
    if settings.database_url.startswith(prefix):
        db_rel = settings.database_url[len(prefix) :]
        db_path = Path(db_rel)
        if not db_path.is_absolute():
            db_path = settings.backend_root / db_rel
        if db_path.exists():
            db_path.unlink()
    init_db()


@pytest.fixture()
def dry_request_payload() -> dict:
    path = settings.backend_root / "app" / "tests" / "fixtures" / "requests" / "search_request_dry_run.json"
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)
