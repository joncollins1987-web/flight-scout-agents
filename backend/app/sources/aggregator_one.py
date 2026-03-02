from __future__ import annotations

import json
from pathlib import Path

from app.core.config import settings
from app.schemas.itinerary import RawItineraryCandidate
from app.schemas.request import SearchRequest
from app.sources._projection import project_candidates_to_request
from app.sources.base import FlightSource, SourceRuntimeConfig


class AggregatorOneSource(FlightSource):
    def __init__(self) -> None:
        self.config = SourceRuntimeConfig(
            name="aggregator_one",
            enabled=settings.source_aggregator_one_enabled,
            timeout_seconds=20,
            max_retries=2,
            backoff_ms=300,
            live_mode=settings.enable_live_sources,
        )

    async def search(self, request: SearchRequest) -> list[RawItineraryCandidate]:
        if not self.config.enabled:
            return []
        if request.dry_run or not self.config.live_mode:
            return project_candidates_to_request(self._fixture_candidates(), request, mode="fixture")
        return self._live_stub_candidates(request)

    def _fixture_candidates(self) -> list[RawItineraryCandidate]:
        path = Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "sources" / "aggregator_one_candidates.json"
        with path.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
        return [RawItineraryCandidate.model_validate(item) for item in data]

    def _live_stub_candidates(self, request: SearchRequest) -> list[RawItineraryCandidate]:
        return project_candidates_to_request(self._fixture_candidates(), request, mode="live")
