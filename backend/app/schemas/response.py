from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.itinerary import NormalizedItinerary


class StopoverPlan(BaseModel):
    model_config = ConfigDict(extra="forbid")

    itinerary_id: str
    layover_airport: str
    usable_time_minutes: int = Field(ge=0)
    transit_time_minutes_est: int = Field(ge=0)
    transit_cost_usd_est: float = Field(ge=0)
    budget_fit: bool | None = None
    bullets: list[str] = Field(min_length=3, max_length=6)
    warnings: list[str] = Field(default_factory=list)


class FinalItineraryItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    itinerary: NormalizedItinerary
    why_bullets: list[str] = Field(default_factory=list)
    stopover_plan: StopoverPlan | None = None


class FinalSearchResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    run_id: str
    generated_at: datetime
    status: Literal["ok", "partial", "warning"]
    cache_hit: bool
    cache_expires_at: datetime | None = None
    warnings: list[str] = Field(default_factory=list)

    cheapest: list[FinalItineraryItem] = Field(default_factory=list)
    nonstop: list[FinalItineraryItem] = Field(default_factory=list)
    strategic: list[FinalItineraryItem] = Field(default_factory=list)

    compare_pool: list[NormalizedItinerary] = Field(default_factory=list)
    metadata: dict[str, str | int | float | bool | None] = Field(default_factory=dict)
