from __future__ import annotations

import json
from pathlib import Path

from app.agents.deduper_normalizer import normalize_and_dedupe
from app.agents.stopover_itinerary import generate_stopover_plans
from app.schemas.itinerary import RawItineraryCandidate
from app.schemas.request import SearchRequest


def test_stopover_plan_created_for_long_layover() -> None:
    source = Path(__file__).resolve().parent / "fixtures" / "sources" / "aggregator_one_candidates.json"
    with source.open("r", encoding="utf-8") as fh:
        rows = json.load(fh)

    candidates = [RawItineraryCandidate.model_validate(row) for row in rows]
    request = SearchRequest(
        destination_query="LAX",
        departure_dates=["2026-05-10"],
        return_dates=["2026-05-17"],
        dry_run=True,
        stopover_plan_enabled=True,
        stopover_leave_airport=True,
    )
    normalized = normalize_and_dedupe(candidates, request).itineraries

    plans = generate_stopover_plans(normalized, request).plans
    assert plans
    assert all(plan.usable_time_minutes >= 0 for plan in plans)
