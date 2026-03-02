from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.itinerary import NormalizedItinerary
from app.schemas.response import FinalItineraryItem, FinalSearchResult, StopoverPlan


class FinalPresenterOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    result: FinalSearchResult


def _as_item(itinerary: NormalizedItinerary, stopover: StopoverPlan | None = None) -> FinalItineraryItem:
    why = itinerary.score.why_bullets if itinerary.score else []
    return FinalItineraryItem(itinerary=itinerary, why_bullets=why, stopover_plan=stopover)


def _sort_cheapest(itineraries: list[NormalizedItinerary]) -> list[NormalizedItinerary]:
    return sorted(itineraries, key=lambda i: (not i.verified, i.true_total_price_usd, i.total_travel_time_minutes))


def _sort_nonstop(itineraries: list[NormalizedItinerary]) -> list[NormalizedItinerary]:
    nonstop = [i for i in itineraries if i.stops_count == 0]
    return sorted(nonstop, key=lambda i: (not i.verified, i.true_total_price_usd, i.total_travel_time_minutes))


def _sort_strategic(itineraries: list[NormalizedItinerary]) -> list[NormalizedItinerary]:
    return sorted(itineraries, key=lambda i: i.score.total_score if i.score else 0.0, reverse=True)


def present_final(
    run_id: str,
    generated_at: datetime,
    itineraries: list[NormalizedItinerary],
    stopover_plans: dict[str, StopoverPlan],
    cache_hit: bool,
    cache_expires_at: datetime | None,
    warnings: list[str],
) -> FinalPresenterOutput:
    cheapest = _sort_cheapest(itineraries)
    nonstop = _sort_nonstop(itineraries)
    strategic = _sort_strategic(itineraries)

    any_verified = any(i.verified for i in itineraries)
    status = "ok"
    if not any_verified:
        status = "warning"
        warnings = warnings + ["No verified itinerary available; showing best unverified options."]
    elif warnings:
        status = "partial"

    result = FinalSearchResult(
        run_id=run_id,
        generated_at=generated_at,
        status=status,
        cache_hit=cache_hit,
        cache_expires_at=cache_expires_at,
        warnings=warnings,
        cheapest=[_as_item(i, stopover_plans.get(i.itinerary_id)) for i in cheapest],
        nonstop=[_as_item(i, stopover_plans.get(i.itinerary_id)) for i in nonstop],
        strategic=[_as_item(i, stopover_plans.get(i.itinerary_id)) for i in strategic],
        compare_pool=strategic[:10],
        metadata={
            "candidate_count": len(itineraries),
            "verified_count": sum(1 for i in itineraries if i.verified),
        },
    )
    return FinalPresenterOutput(result=result)
