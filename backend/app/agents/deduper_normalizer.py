from __future__ import annotations

import hashlib
from datetime import timedelta

from pydantic import BaseModel, ConfigDict, Field

from app.core.booking_links import ensure_actionable_booking_url
from app.core.pricing import estimate_true_total_from_raw
from app.schemas.itinerary import FlightSegment, NormalizedItinerary, RawItineraryCandidate
from app.schemas.request import SearchRequest


class NormalizedCandidateSet(BaseModel):
    model_config = ConfigDict(extra="forbid")

    itineraries: list[NormalizedItinerary] = Field(default_factory=list)


def _stops_count(segments: list[FlightSegment]) -> int:
    return max(0, len(segments) - 1)


def _layovers(segments: list[FlightSegment]) -> list[int]:
    layovers: list[int] = []
    if len(segments) <= 1:
        return layovers
    for idx in range(len(segments) - 1):
        delta: timedelta = segments[idx + 1].departure_time_utc - segments[idx].arrival_time_utc
        layovers.append(max(0, int(delta.total_seconds() // 60)))
    return layovers


def _route_key(candidate: RawItineraryCandidate) -> str:
    outbound = "|".join(f"{seg.carrier}:{seg.flight_number}" for seg in candidate.segments_outbound)
    inbound = "|".join(f"{seg.carrier}:{seg.flight_number}" for seg in candidate.segments_inbound)
    return f"{candidate.origin_airport}-{candidate.destination_airport}:{candidate.depart_date}:{candidate.return_date}:{outbound}:{inbound}"


def _canonical_id(route_key: str) -> str:
    return hashlib.sha1(route_key.encode("utf-8")).hexdigest()[:16]


def normalize_and_dedupe(candidates: list[RawItineraryCandidate], request: SearchRequest) -> NormalizedCandidateSet:
    grouped: dict[str, list[RawItineraryCandidate]] = {}
    for candidate in candidates:
        grouped.setdefault(_route_key(candidate), []).append(candidate)

    normalized: list[NormalizedItinerary] = []

    for key, group in grouped.items():
        primary = min(group, key=lambda g: g.base_fare_usd + g.taxes_fees_usd)

        all_segments = primary.segments_outbound + primary.segments_inbound
        stops = _stops_count(primary.segments_outbound) + _stops_count(primary.segments_inbound)

        layovers = _layovers(primary.segments_outbound) + _layovers(primary.segments_inbound)
        longest_layover = max(layovers) if layovers else 0
        tight_connection = any(minutes < 60 for minutes in layovers)

        total_travel = sum(seg.duration_minutes for seg in all_segments) + sum(layovers)
        estimated_true = estimate_true_total_from_raw(primary, request)

        first_depart_time = primary.segments_outbound[0].departure_time_utc.time()
        last_arrive_time = primary.segments_inbound[-1].arrival_time_utc.time()
        red_eye = first_depart_time.hour < 6 or last_arrive_time.hour < 6

        normalized.append(
            NormalizedItinerary(
                itinerary_id=_canonical_id(key),
                source="multi" if len({g.source for g in group}) > 1 else primary.source,
                source_candidate_ids=[g.candidate_id for g in group],
                booking_url=ensure_actionable_booking_url(
                    primary.booking_url,
                    origin=primary.origin_airport,
                    destination=primary.destination_airport,
                    depart_date=primary.depart_date,
                    return_date=primary.return_date,
                    adults=request.passengers_adults,
                    cabin=request.cabin,
                    currency=request.currency,
                ),
                origin_airport=primary.origin_airport,
                destination_airport=primary.destination_airport,
                depart_date=primary.depart_date,
                return_date=primary.return_date,
                segments_outbound=primary.segments_outbound,
                segments_inbound=primary.segments_inbound,
                base_fare_usd=primary.base_fare_usd,
                taxes_fees_usd=primary.taxes_fees_usd,
                estimated_true_total_usd=estimated_true,
                true_total_price_usd=estimated_true,
                fare_brand=primary.fare_brand,
                refundable=primary.refundable,
                baggage_rules_summary=f"{primary.bags_included} bag(s) included by fare.",
                seat_cost_summary="Seat selection included" if primary.seat_selection_included else "Seat fee may apply",
                change_cancel_summary="Refundable" if primary.refundable else "Change/cancel penalties may apply",
                stops_count=stops,
                total_travel_time_minutes=total_travel,
                longest_layover_minutes=longest_layover,
                self_transfer=primary.self_transfer,
                tight_connection=tight_connection,
                red_eye=red_eye,
                first_depart_local_time=first_depart_time,
                last_arrive_local_time=last_arrive_time,
                gotchas=[],
                policy_flags={},
            )
        )

    return NormalizedCandidateSet(itineraries=normalized)
