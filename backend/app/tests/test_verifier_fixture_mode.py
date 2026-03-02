from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.agents.deduper_normalizer import normalize_and_dedupe
from app.agents.verifier import verify_itineraries
from app.core.artifact_store import ArtifactStore
from app.schemas.itinerary import RawItineraryCandidate
from app.schemas.request import SearchRequest


@pytest.mark.asyncio
async def test_verifier_produces_verified_rows_in_dry_run() -> None:
    fixtures = Path(__file__).resolve().parent / "fixtures" / "sources"
    rows = []
    for name in ["aggregator_one_candidates.json", "aggregator_two_candidates.json"]:
        with (fixtures / name).open("r", encoding="utf-8") as fh:
            rows.extend(json.load(fh))

    candidates = [RawItineraryCandidate.model_validate(row) for row in rows]
    request = SearchRequest(
        destination_query="LAX",
        departure_dates=["2026-05-10"],
        return_dates=["2026-05-17"],
        dry_run=True,
    )

    normalized = normalize_and_dedupe(candidates, request).itineraries[:3]
    batch = await verify_itineraries(normalized, request, ArtifactStore("test-verifier"))

    assert batch.verified
    assert all(v.status in {"verified", "failed"} for v in batch.verified)
    assert any(v.verified for v in batch.verified)
