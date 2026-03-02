from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.itinerary import RawItineraryCandidate


class ScoutAggregatorOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source: str
    candidates: list[RawItineraryCandidate] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
