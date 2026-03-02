from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.itinerary import NormalizedItinerary
from app.schemas.request import SearchRequest
from app.schemas.response import StopoverPlan


class StopoverBatch(BaseModel):
    model_config = ConfigDict(extra="forbid")

    plans: list[StopoverPlan] = Field(default_factory=list)


def generate_stopover_plans(itineraries: list[NormalizedItinerary], request: SearchRequest) -> StopoverBatch:
    plans: list[StopoverPlan] = []
    if not request.stopover_plan_enabled:
        return StopoverBatch(plans=[])

    for itinerary in itineraries:
        layover = itinerary.longest_layover_minutes or 0
        if layover <= 360:
            continue
        transit = 70 if request.stopover_leave_airport else 30
        usable = max(0, layover - transit)
        transit_cost = 30.0 if request.stopover_leave_airport else 0.0
        budget_fit = None
        if request.stopover_budget_usd is not None:
            budget_fit = transit_cost <= request.stopover_budget_usd

        effort_note = {
            "low": "Stay airport-adjacent with minimal transfers.",
            "medium": "One nearby district visit with buffer time.",
            "high": "Two short activities with strict return timing.",
        }[request.stopover_effort]

        bullets = [
            f"Usable stopover time is about {usable} minutes after transfer/security buffer.",
            f"Estimated transit: {transit} minutes round trip, about ${transit_cost:.2f}.",
            effort_note,
        ]
        if request.stopover_budget_usd is not None:
            bullets.append(f"Plan targets budget cap ${request.stopover_budget_usd:.2f}.")

        warnings = []
        if request.stopover_leave_airport and layover < 480:
            warnings.append("Leave-airport plan is tight; re-enter security early.")

        plans.append(
            StopoverPlan(
                itinerary_id=itinerary.itinerary_id,
                layover_airport=itinerary.destination_airport,
                usable_time_minutes=usable,
                transit_time_minutes_est=transit,
                transit_cost_usd_est=transit_cost,
                budget_fit=budget_fit,
                bullets=bullets,
                warnings=warnings,
            )
        )

    return StopoverBatch(plans=plans)
