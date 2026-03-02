from __future__ import annotations

import json
from pathlib import Path

from app.agents.deduper_normalizer import normalize_and_dedupe
from app.core.scoring import compute_score_breakdown
from app.schemas.itinerary import RawItineraryCandidate
from app.schemas.request import SearchRequest


def test_scoring_applies_red_eye_penalty_when_enabled() -> None:
    source = Path(__file__).resolve().parent / "fixtures" / "sources" / "aggregator_two_candidates.json"
    with source.open("r", encoding="utf-8") as fh:
        rows = json.load(fh)

    candidates = [RawItineraryCandidate.model_validate(row) for row in rows]
    request = SearchRequest(
        destination_query="LAX",
        departure_dates=["2026-05-10"],
        return_dates=["2026-05-17"],
        dry_run=True,
        avoid_red_eyes=True,
    )
    normalized = normalize_and_dedupe(candidates, request).itineraries
    red_eye = next(item for item in normalized if item.red_eye)

    score = compute_score_breakdown(red_eye, request)
    assert score.red_eye_penalty > 0
    assert len(score.why_bullets) >= 2
