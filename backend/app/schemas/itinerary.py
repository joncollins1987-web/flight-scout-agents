from __future__ import annotations

from datetime import date, datetime, time

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.scoring import ScoreBreakdown
from app.schemas.verification import VerificationEvidence


class FlightSegment(BaseModel):
    model_config = ConfigDict(extra="forbid")

    carrier: str
    flight_number: str
    origin_airport: str
    destination_airport: str
    departure_time_utc: datetime
    arrival_time_utc: datetime
    duration_minutes: int = Field(ge=1)
    origin_terminal: str | None = None
    destination_terminal: str | None = None

    @field_validator("origin_airport", "destination_airport", mode="before")
    @classmethod
    def normalize_airport(cls, value: str) -> str:
        return value.strip().upper()


class RawItineraryCandidate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    candidate_id: str
    source: str
    booking_url: str

    origin_airport: str
    destination_airport: str
    depart_date: date
    return_date: date

    segments_outbound: list[FlightSegment] = Field(min_length=1)
    segments_inbound: list[FlightSegment] = Field(min_length=1)

    base_fare_usd: float = Field(ge=0)
    taxes_fees_usd: float = Field(default=0, ge=0)
    headline_price_usd: float | None = Field(default=None, ge=0)

    fare_brand: str | None = None
    refundable: bool = False
    cabin: str = "economy"

    bags_included: int = Field(default=0, ge=0)
    seat_selection_included: bool = False

    self_transfer: bool = False
    parsing_confidence: float = Field(ge=0, le=1)
    raw_notes: list[str] = Field(default_factory=list)


class NormalizedItinerary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    itinerary_id: str
    source: str
    source_candidate_ids: list[str] = Field(min_length=1)
    booking_url: str | None = None

    origin_airport: str
    destination_airport: str
    depart_date: date
    return_date: date

    segments_outbound: list[FlightSegment] = Field(min_length=1)
    segments_inbound: list[FlightSegment] = Field(min_length=1)

    base_fare_usd: float = Field(ge=0)
    taxes_fees_usd: float = Field(ge=0)
    estimated_true_total_usd: float = Field(ge=0)
    true_total_price_usd: float = Field(ge=0)

    fare_brand: str | None = None
    refundable: bool = False
    baggage_rules_summary: str | None = None
    seat_cost_summary: str | None = None
    change_cancel_summary: str | None = None

    stops_count: int = Field(ge=0)
    total_travel_time_minutes: int = Field(ge=1)
    longest_layover_minutes: int | None = Field(default=None, ge=0)

    self_transfer: bool = False
    tight_connection: bool = False
    red_eye: bool = False
    first_depart_local_time: time | None = None
    last_arrive_local_time: time | None = None

    gotchas: list[str] = Field(default_factory=list)
    policy_flags: dict[str, bool] = Field(default_factory=dict)

    verified: bool = False
    verified_at: datetime | None = None
    verified_total_price_usd: float | None = Field(default=None, ge=0)
    verification_status: str = "unverified"
    verification_material_change: bool = False
    verification_evidence: VerificationEvidence | None = None

    score: ScoreBreakdown | None = None
