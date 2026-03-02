from __future__ import annotations

from datetime import date, time
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


DEFAULT_ORIGINS = ["JFK", "EWR", "LGA"]
DEFAULT_NEARBY = ["HPN", "ISP", "PHL"]
DEFAULT_SOURCE_FLAGS = {
    "aggregator_one": True,
    "aggregator_two": True,
}


class SearchRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    origin_airports: list[str] = Field(default_factory=lambda: DEFAULT_ORIGINS.copy(), min_length=1)
    include_nearby_airports: bool = False
    nearby_airports: list[str] = Field(default_factory=lambda: DEFAULT_NEARBY.copy())
    nearby_radius_miles: int | None = Field(default=None, ge=1, le=300)

    destination_query: str = Field(min_length=2)
    departure_dates: list[date] = Field(min_length=1)
    return_dates: list[date] = Field(min_length=1)

    passengers_adults: int = Field(default=1, ge=1, le=9)
    cabin: Literal["economy", "premium_economy", "business", "first"] = "economy"
    currency: Literal["USD"] = "USD"

    carry_on_count: int = Field(default=0, ge=0, le=5)
    checked_bag_count: int = Field(default=0, ge=0, le=5)

    basic_economy_allowed: bool = True
    refundable_required: bool = False

    earliest_depart_local: time | None = None
    latest_arrive_local: time | None = None

    allow_stopovers: bool = True
    max_layover_minutes: int | None = Field(default=None, ge=30, le=1440)
    prefer_nonstop: bool = False

    stopover_plan_enabled: bool = False
    stopover_budget_usd: float | None = Field(default=None, ge=0)
    stopover_effort: Literal["low", "medium", "high"] = "medium"
    stopover_leave_airport: bool = False

    avoid_red_eyes: bool = False
    avoid_tight_connections: bool = False
    preferred_airlines: list[str] = Field(default_factory=list)
    blocked_airlines: list[str] = Field(default_factory=list)

    dry_run: bool = False
    max_verify_per_tab: int = Field(default=5, ge=3, le=10)
    source_flags: dict[str, bool] = Field(default_factory=lambda: DEFAULT_SOURCE_FLAGS.copy())

    @field_validator("origin_airports", "nearby_airports", mode="before")
    @classmethod
    def normalize_airports(cls, value: list[str] | str) -> list[str]:
        if isinstance(value, str):
            value = [value]
        return [v.strip().upper() for v in value if v and v.strip()]

    @field_validator("preferred_airlines", "blocked_airlines", mode="before")
    @classmethod
    def normalize_airlines(cls, value: list[str] | str) -> list[str]:
        if isinstance(value, str):
            value = [value]
        return [v.strip().upper() for v in value if v and v.strip()]

    @field_validator("destination_query", mode="before")
    @classmethod
    def normalize_destination(cls, value: str) -> str:
        return value.strip().upper()

    @model_validator(mode="after")
    def validate_dates(self) -> "SearchRequest":
        if min(self.return_dates) < min(self.departure_dates):
            raise ValueError("return_dates must be on/after departure_dates")
        return self
