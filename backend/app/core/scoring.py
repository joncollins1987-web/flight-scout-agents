from __future__ import annotations

from dataclasses import dataclass
from datetime import time

from app.schemas.itinerary import NormalizedItinerary
from app.schemas.request import SearchRequest
from app.schemas.scoring import ScoreBreakdown


@dataclass(frozen=True)
class ScoreWeights:
    price: float = 0.45
    travel_time: float = 0.25
    convenience: float = 0.15
    connection_risk: float = 0.10
    red_eye: float = 0.05


def _window_penalty(itinerary: NormalizedItinerary, earliest: time | None, latest: time | None) -> float:
    penalty = 0.0
    if earliest and itinerary.first_depart_local_time and itinerary.first_depart_local_time < earliest:
        penalty += 20.0
    if latest and itinerary.last_arrive_local_time and itinerary.last_arrive_local_time > latest:
        penalty += 20.0
    return penalty


def _connection_risk(itinerary: NormalizedItinerary, request: SearchRequest) -> float:
    risk = 0.0
    if itinerary.self_transfer:
        risk += 25.0
    if itinerary.tight_connection:
        risk += 20.0
    if itinerary.longest_layover_minutes and itinerary.longest_layover_minutes > 360:
        risk += 10.0
    if request.avoid_tight_connections and itinerary.tight_connection:
        risk += 15.0
    return risk


def compute_score_breakdown(itinerary: NormalizedItinerary, request: SearchRequest) -> ScoreBreakdown:
    weights = ScoreWeights()
    price_component = itinerary.true_total_price_usd * weights.price
    duration_component = itinerary.total_travel_time_minutes * weights.travel_time * 0.03
    convenience_component = _window_penalty(itinerary, request.earliest_depart_local, request.latest_arrive_local) * weights.convenience
    connection_component = _connection_risk(itinerary, request) * weights.connection_risk
    red_eye_component = (15.0 if itinerary.red_eye and request.avoid_red_eyes else 0.0) * weights.red_eye

    raw_cost = price_component + duration_component + convenience_component + connection_component + red_eye_component
    total_score = round(max(0.0, 1000.0 - raw_cost), 2)

    why = [
        f"True total ${itinerary.true_total_price_usd:.2f} with fees accounted.",
        f"Total travel time {itinerary.total_travel_time_minutes} minutes.",
    ]
    if itinerary.stops_count == 0:
        why.append("Nonstop routing reduces disruption risk.")
    if itinerary.verified:
        why.append("Price and fare details verified in this run.")
    if len(why) > 4:
        why = why[:4]

    return ScoreBreakdown(
        itinerary_id=itinerary.itinerary_id,
        total_price_true=round(price_component, 2),
        total_travel_time_minutes=round(duration_component, 2),
        convenience_vs_windows=round(convenience_component, 2),
        connection_risk=round(connection_component, 2),
        red_eye_penalty=round(red_eye_component, 2),
        total_score=total_score,
        why_bullets=why,
    )


def attach_scores(itineraries: list[NormalizedItinerary], request: SearchRequest) -> list[NormalizedItinerary]:
    scored: list[NormalizedItinerary] = []
    for itinerary in itineraries:
        breakdown = compute_score_breakdown(itinerary, request)
        scored.append(itinerary.model_copy(update={"score": breakdown}))
    return scored
