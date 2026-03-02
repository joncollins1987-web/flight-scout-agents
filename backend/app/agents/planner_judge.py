from __future__ import annotations

from datetime import date

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.request import SearchRequest


class DatePair(BaseModel):
    model_config = ConfigDict(extra="forbid")

    depart_date: date
    return_date: date


class PlannerJudgeOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    expanded_date_pairs: list[DatePair] = Field(default_factory=list)
    scoring_weights: dict[str, float]
    verification_top_n: int = Field(ge=3)
    source_dispatch: list[str]
    policies: list[str] = Field(default_factory=list)


def local_plan(request: SearchRequest) -> PlannerJudgeOutput:
    pairs: list[DatePair] = []
    for depart in request.departure_dates:
        for ret in request.return_dates:
            if ret >= depart:
                pairs.append(DatePair(depart_date=depart, return_date=ret))

    source_dispatch = []
    if request.source_flags.get("aggregator_one", True):
        source_dispatch.append("aggregator_one")
    if request.source_flags.get("aggregator_two", True):
        source_dispatch.append("aggregator_two")

    policies = [
        "Top candidates per tab require in-run verification.",
        "Cheapest ranking is based on true total cost.",
    ]
    if request.stopover_plan_enabled:
        policies.append("Generate stopover plans for layovers over 6h.")

    return PlannerJudgeOutput(
        expanded_date_pairs=pairs,
        scoring_weights={
            "total_price_true": 0.45,
            "total_travel_time_minutes": 0.25,
            "convenience_vs_windows": 0.15,
            "connection_risk": 0.10,
            "red_eye_penalty": 0.05,
        },
        verification_top_n=max(3, request.max_verify_per_tab),
        source_dispatch=source_dispatch,
        policies=policies,
    )
