from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.schemas.itinerary import RawItineraryCandidate
from app.schemas.request import SearchRequest


@dataclass(frozen=True)
class SourceRuntimeConfig:
    name: str
    enabled: bool
    timeout_seconds: int = 20
    max_retries: int = 2
    backoff_ms: int = 300
    live_mode: bool = False


class FlightSource(ABC):
    config: SourceRuntimeConfig

    @abstractmethod
    async def search(self, request: SearchRequest) -> list[RawItineraryCandidate]:
        raise NotImplementedError
