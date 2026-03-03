from __future__ import annotations

from app.core.booking_links import ensure_actionable_booking_url, is_placeholder_booking_url
from app.schemas.itinerary import NormalizedItinerary, RawItineraryCandidate
from app.schemas.request import SearchRequest
from app.schemas.verification import VerifiedItinerary


DEFAULT_CARRY_ON_FEE_USD = 35.0
DEFAULT_CHECKED_BAG_FEE_USD = 45.0
DEFAULT_SEAT_FEE_USD = 20.0


def estimate_true_total_from_raw(candidate: RawItineraryCandidate, request: SearchRequest) -> float:
    bag_cost = (request.carry_on_count * DEFAULT_CARRY_ON_FEE_USD) + (
        request.checked_bag_count * DEFAULT_CHECKED_BAG_FEE_USD
    )
    seat_cost = 0.0 if candidate.seat_selection_included else DEFAULT_SEAT_FEE_USD
    mandatory_fare_cost = 0.0
    if request.refundable_required and not candidate.refundable:
        mandatory_fare_cost += 80.0
    return round(candidate.base_fare_usd + candidate.taxes_fees_usd + bag_cost + seat_cost + mandatory_fare_cost, 2)


def true_total_for_normalized(itinerary: NormalizedItinerary) -> float:
    if itinerary.verified_total_price_usd is not None:
        return itinerary.verified_total_price_usd
    return itinerary.estimated_true_total_usd


def _pick_booking_url(itinerary_url: str | None, evidence_url: str | None) -> str | None:
    if evidence_url and not is_placeholder_booking_url(evidence_url):
        return evidence_url
    if itinerary_url and not is_placeholder_booking_url(itinerary_url):
        return itinerary_url
    # Keep raw itinerary URL as a fallback when no actionable link exists yet.
    return itinerary_url


def apply_verification_to_normalized(
    itinerary: NormalizedItinerary, verified: VerifiedItinerary | None
) -> NormalizedItinerary:
    if verified is None:
        return itinerary
    booking_url = ensure_actionable_booking_url(
        _pick_booking_url(
            itinerary_url=itinerary.booking_url,
            evidence_url=verified.evidence.checked_url if verified.evidence else None,
        ),
        origin=itinerary.origin_airport,
        destination=itinerary.destination_airport,
        depart_date=itinerary.depart_date,
        return_date=itinerary.return_date,
        adults=1,
        cabin="economy",
        currency="USD",
    )
    return itinerary.model_copy(
        update={
            "verified": verified.verified,
            "verified_at": verified.evidence.verified_at if verified.evidence else None,
            "verified_total_price_usd": verified.verified_total_price_usd,
            "booking_url": booking_url,
            "fare_brand": verified.fare_brand or itinerary.fare_brand,
            "baggage_rules_summary": verified.baggage_rules_summary or itinerary.baggage_rules_summary,
            "seat_cost_summary": verified.seat_cost_summary or itinerary.seat_cost_summary,
            "change_cancel_summary": verified.change_cancel_summary or itinerary.change_cancel_summary,
            "verification_status": verified.status,
            "verification_material_change": verified.material_price_change,
            "verification_evidence": verified.evidence,
        }
    )
