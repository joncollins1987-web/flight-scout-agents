from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from app.core.scoring import attach_scores
from app.schemas.itinerary import NormalizedItinerary
from app.schemas.request import SearchRequest


class StrategicRankOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    itineraries: list[NormalizedItinerary] = Field(default_factory=list)


def rank_itineraries(itineraries: list[NormalizedItinerary], request: SearchRequest) -> StrategicRankOutput:
    return StrategicRankOutput(itineraries=attach_scores(itineraries, request))
