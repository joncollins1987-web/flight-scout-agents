from __future__ import annotations

import pytest

from app.schemas.request import SearchRequest
from app.sources.aggregator_one import AggregatorOneSource
from app.sources.aggregator_two import AggregatorTwoSource


@pytest.mark.asyncio
async def test_sources_return_fixture_candidates_in_dry_run() -> None:
    request = SearchRequest(
        destination_query="LAX",
        departure_dates=["2026-05-10"],
        return_dates=["2026-05-17"],
        dry_run=True,
    )
    one = AggregatorOneSource()
    two = AggregatorTwoSource()

    one_results = await one.search(request)
    two_results = await two.search(request)

    assert one_results
    assert two_results
    assert all(item.source == "aggregator_one" for item in one_results)
    assert all(item.source == "aggregator_two" for item in two_results)

    for item in one_results + two_results:
        assert item.destination_airport == "LAX"
        assert item.depart_date.isoformat() == "2026-05-10"
        assert item.return_date.isoformat() == "2026-05-17"
        assert item.segments_outbound[0].departure_time_utc.date().isoformat() == "2026-05-10"
        assert item.segments_inbound[0].departure_time_utc.date().isoformat() == "2026-05-17"
