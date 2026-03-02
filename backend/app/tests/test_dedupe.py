from __future__ import annotations

import json
from pathlib import Path

from app.agents.deduper_normalizer import normalize_and_dedupe
from app.schemas.itinerary import RawItineraryCandidate
from app.schemas.request import SearchRequest


def test_dedupe_reduces_duplicate_routes() -> None:
    base = Path(__file__).resolve().parent / "fixtures" / "sources"
    data = []
    for name in ["aggregator_one_candidates.json", "aggregator_two_candidates.json"]:
        with (base / name).open("r", encoding="utf-8") as fh:
            data.extend(json.load(fh))

    candidates = [RawItineraryCandidate.model_validate(row) for row in data]
    request = SearchRequest(
        destination_query="LAX",
        departure_dates=["2026-05-10"],
        return_dates=["2026-05-17"],
        dry_run=True,
    )

    output = normalize_and_dedupe(candidates, request)
    assert len(output.itineraries) < len(candidates)
    assert any(i.longest_layover_minutes and i.longest_layover_minutes > 360 for i in output.itineraries)
