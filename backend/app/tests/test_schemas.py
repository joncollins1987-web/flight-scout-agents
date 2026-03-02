from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.schemas.request import SearchRequest


def test_search_request_defaults_and_normalization() -> None:
    request = SearchRequest(
        destination_query=" lax ",
        departure_dates=["2026-05-10"],
        return_dates=["2026-05-17"],
    )
    assert request.origin_airports == ["JFK", "EWR", "LGA"]
    assert request.destination_query == "LAX"
    assert request.max_verify_per_tab == 5


def test_search_request_forbids_extra_fields() -> None:
    with pytest.raises(ValidationError):
        SearchRequest(
            destination_query="LAX",
            departure_dates=["2026-05-10"],
            return_dates=["2026-05-17"],
            unknown_field="x",
        )
