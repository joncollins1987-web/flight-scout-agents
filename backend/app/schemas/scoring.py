from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ScoreBreakdown(BaseModel):
    model_config = ConfigDict(extra="forbid")

    itinerary_id: str
    total_price_true: float = Field(ge=0)
    total_travel_time_minutes: float = Field(ge=0)
    convenience_vs_windows: float = Field(ge=0)
    connection_risk: float = Field(ge=0)
    red_eye_penalty: float = Field(ge=0)
    total_score: float = Field(ge=0)
    why_bullets: list[str] = Field(min_length=2, max_length=4)
