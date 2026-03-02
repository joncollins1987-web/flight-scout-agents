from __future__ import annotations

from pathlib import Path

from sqlmodel import SQLModel, create_engine

from app.core.config import settings


def _ensure_sqlite_dir(url: str) -> None:
    prefix = "sqlite:///"
    if not url.startswith(prefix):
        return
    raw_path = url[len(prefix) :]
    path = Path(raw_path)
    if not path.is_absolute():
        path = settings.backend_root / raw_path
    path.parent.mkdir(parents=True, exist_ok=True)


_ensure_sqlite_dir(settings.database_url)
engine = create_engine(settings.database_url, echo=False)


def init_db() -> None:
    SQLModel.metadata.create_all(engine)
