from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

from app.core.booking_links import ensure_actionable_booking_url, is_placeholder_booking_url
from app.schemas.itinerary import FlightSegment, RawItineraryCandidate
from app.schemas.request import SearchRequest


def _destination_code(query: str) -> str:
    value = query.strip().upper()
    if len(value) <= 3:
        return value
    return value[:3]


def _retarget_segments(
    segments: list[FlightSegment],
    new_origin: str,
    new_destination: str,
) -> list[FlightSegment]:
    updated: list[FlightSegment] = []
    for index, segment in enumerate(segments):
        patch: dict[str, str] = {}
        if index == 0:
            patch["origin_airport"] = new_origin
        if index == len(segments) - 1:
            patch["destination_airport"] = new_destination
        updated.append(segment.model_copy(update=patch) if patch else segment)
    return updated


def _parse_utc(iso_value: str | datetime) -> datetime:
    if isinstance(iso_value, datetime):
        return iso_value.astimezone(timezone.utc)
    return datetime.fromisoformat(iso_value.replace("Z", "+00:00")).astimezone(timezone.utc)


def _retime_segments(segments: list[FlightSegment], anchor_date: date) -> list[FlightSegment]:
    if not segments:
        return []

    anchor_departure = _parse_utc(segments[0].departure_time_utc)
    updated: list[FlightSegment] = []
    for segment in segments:
        dep = _parse_utc(segment.departure_time_utc)
        arr = _parse_utc(segment.arrival_time_utc)
        dep_day_offset = (dep.date() - anchor_departure.date()).days
        arr_day_offset = (arr.date() - anchor_departure.date()).days

        dep_date = anchor_date + timedelta(days=dep_day_offset)
        arr_date = anchor_date + timedelta(days=arr_day_offset)

        new_dep = datetime.combine(dep_date, dep.timetz()).astimezone(timezone.utc)
        new_arr = datetime.combine(arr_date, arr.timetz()).astimezone(timezone.utc)

        updated.append(
            segment.model_copy(
                update={
                    "departure_time_utc": new_dep,
                    "arrival_time_utc": new_arr,
                }
            )
        )
    return updated


def _prefilled_booking_url(
    base_url: str,
    origin: str,
    destination: str,
    depart_date: date,
    return_date: date,
    request: SearchRequest,
) -> str:
    if is_placeholder_booking_url(base_url):
        return ensure_actionable_booking_url(
            None,
            origin=origin,
            destination=destination,
            depart_date=depart_date,
            return_date=return_date,
            adults=request.passengers_adults,
            cabin=request.cabin,
            currency=request.currency,
        )

    parsed = urlparse(base_url)
    existing = parse_qs(parsed.query, keep_blank_values=True)
    existing.update(
        {
            "origin": [origin],
            "destination": [destination],
            "depart": [depart_date.isoformat()],
            "return": [return_date.isoformat()],
            "adults": [str(request.passengers_adults)],
            "cabin": [request.cabin],
            "currency": [request.currency],
            "carry_on": [str(request.carry_on_count)],
            "checked_bags": [str(request.checked_bag_count)],
        }
    )
    query = urlencode(existing, doseq=True)
    return urlunparse(parsed._replace(query=query))


def project_candidates_to_request(
    candidates: list[RawItineraryCandidate],
    request: SearchRequest,
    mode: str,
) -> list[RawItineraryCandidate]:
    if not candidates:
        return []

    destination = _destination_code(request.destination_query)
    origins = request.origin_airports or ["JFK"]
    depart_dates = request.departure_dates or [date.today()]
    return_dates = request.return_dates or depart_dates

    projected: list[RawItineraryCandidate] = []

    for index, candidate in enumerate(candidates):
        origin = origins[index % len(origins)]
        depart_date = depart_dates[index % len(depart_dates)]
        return_date = return_dates[index % len(return_dates)]

        outbound = _retime_segments(
            _retarget_segments(candidate.segments_outbound, origin, destination),
            depart_date,
        )
        inbound = _retime_segments(
            _retarget_segments(candidate.segments_inbound, destination, origin),
            return_date,
        )

        projected.append(
            candidate.model_copy(
                update={
                    "candidate_id": f"{candidate.candidate_id}-{origin}-{destination}-{mode}",
                    "booking_url": _prefilled_booking_url(
                        candidate.booking_url,
                        origin,
                        destination,
                        depart_date,
                        return_date,
                        request,
                    ),
                    "origin_airport": origin,
                    "destination_airport": destination,
                    "depart_date": depart_date,
                    "return_date": return_date,
                    "segments_outbound": outbound,
                    "segments_inbound": inbound,
                }
            )
        )

    return projected
