from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _bool(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./data/flight_scout.db")
    cache_ttl_minutes: int = int(os.getenv("CACHE_TTL_MINUTES", "45"))
    verify_top_n_per_tab: int = int(os.getenv("VERIFY_TOP_N_PER_TAB", "5"))
    verification_stale_minutes: int = int(os.getenv("VERIFICATION_STALE_MINUTES", "30"))
    source_aggregator_one_enabled: bool = _bool(os.getenv("SOURCE_AGGREGATOR_ONE_ENABLED"), True)
    source_aggregator_two_enabled: bool = _bool(os.getenv("SOURCE_AGGREGATOR_TWO_ENABLED"), True)
    enable_live_sources: bool = _bool(os.getenv("ENABLE_LIVE_SOURCES"), False)
    playwright_headless: bool = _bool(os.getenv("PLAYWRIGHT_HEADLESS"), True)
    playwright_timeout_ms: int = int(os.getenv("PLAYWRIGHT_TIMEOUT_MS", "30000"))
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

    @property
    def backend_root(self) -> Path:
        return Path(__file__).resolve().parents[2]

    @property
    def runs_dir(self) -> Path:
        path = self.backend_root / "runs"
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def data_dir(self) -> Path:
        path = self.backend_root / "data"
        path.mkdir(parents=True, exist_ok=True)
        return path


settings = Settings()
