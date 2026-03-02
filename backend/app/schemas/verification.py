from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class VerificationEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid")

    verified_at: datetime
    checked_url: str
    price_text_snapshot: str
    fare_brand_text: str | None = None
    baggage_rules_text: str | None = None
    seat_fee_text: str | None = None
    change_cancel_text: str | None = None
    screenshot_path: str | None = None


class VerifiedItinerary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    itinerary_id: str
    source: str
    status: Literal["verified", "failed", "unverified"]
    verified: bool = False
    verified_total_price_usd: float | None = Field(default=None, ge=0)
    fare_brand: str | None = None
    baggage_rules_summary: str | None = None
    seat_cost_summary: str | None = None
    change_cancel_summary: str | None = None
    material_price_change: bool = False
    evidence: VerificationEvidence | None = None
    failure_reason: str | None = None
