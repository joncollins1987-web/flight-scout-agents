from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.itinerary import NormalizedItinerary
from app.schemas.request import SearchRequest


class ConstraintsOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    itineraries: list[NormalizedItinerary] = Field(default_factory=list)


def apply_constraints(itineraries: list[NormalizedItinerary], request: SearchRequest) -> ConstraintsOutput:
    constrained: list[NormalizedItinerary] = []

    for itinerary in itineraries:
        gotchas = itinerary.gotchas.copy()
        flags = dict(itinerary.policy_flags)

        fare_brand = (itinerary.fare_brand or "").lower()
        if not request.basic_economy_allowed and "basic" in fare_brand:
            gotchas.append("Basic economy fare is not allowed by request.")
            flags["violates_basic_economy"] = True

        if request.refundable_required and not itinerary.refundable:
            gotchas.append("Fare is not refundable.")
            flags["violates_refundable"] = True

        if request.max_layover_minutes and itinerary.longest_layover_minutes and itinerary.longest_layover_minutes > request.max_layover_minutes:
            gotchas.append("Layover exceeds requested maximum.")
            flags["violates_layover_max"] = True

        if itinerary.self_transfer:
            gotchas.append("Self-transfer requires separate check-in/baggage handling.")
            flags["self_transfer"] = True

        if itinerary.tight_connection:
            gotchas.append("Tight connection window may increase misconnect risk.")
            flags["tight_connection"] = True

        if request.stopover_leave_airport and itinerary.longest_layover_minutes and itinerary.longest_layover_minutes < 240:
            gotchas.append("Limited time to safely leave the airport on this layover.")
            flags["leave_airport_risky"] = True

        constrained.append(itinerary.model_copy(update={"gotchas": gotchas, "policy_flags": flags}))

    return ConstraintsOutput(itineraries=constrained)
