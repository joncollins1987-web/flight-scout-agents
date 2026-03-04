from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app
from app.schemas.response import FinalSearchResult


def test_api_search_dry_run_shape_and_cache(dry_request_payload: dict) -> None:
    client = TestClient(app)

    first = client.post("/api/search", json=dry_request_payload)
    assert first.status_code == 200
    parsed_one = FinalSearchResult.model_validate(first.json())
    assert parsed_one.cheapest
    assert parsed_one.strategic
    assert any(item.itinerary.verified for item in parsed_one.cheapest)
    assert parsed_one.metadata.get("data_mode") == "fixtures"
    assert parsed_one.metadata.get("request_dry_run") is True

    second = client.post("/api/search", json=dry_request_payload)
    assert second.status_code == 200
    parsed_two = FinalSearchResult.model_validate(second.json())
    assert parsed_two.cache_hit is True
    assert parsed_two.run_id != parsed_one.run_id
