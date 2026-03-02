from __future__ import annotations

from app.schemas.itinerary import NormalizedItinerary


def compare_itineraries(a: NormalizedItinerary, b: NormalizedItinerary) -> list[str]:
    bullets: list[str] = []
    price_diff = round(a.true_total_price_usd - b.true_total_price_usd, 2)
    if price_diff != 0:
        winner = a.itinerary_id if price_diff < 0 else b.itinerary_id
        bullets.append(f"{winner} is ${abs(price_diff):.2f} cheaper in true total cost.")
    time_diff = abs(a.total_travel_time_minutes - b.total_travel_time_minutes)
    if time_diff:
        faster = a.itinerary_id if a.total_travel_time_minutes < b.total_travel_time_minutes else b.itinerary_id
        bullets.append(f"{faster} is {time_diff} minutes faster total travel time.")
    if a.refundable != b.refundable:
        refundable = a.itinerary_id if a.refundable else b.itinerary_id
        bullets.append(f"{refundable} has refundable fare rules.")
    if a.stops_count != b.stops_count:
        fewer = a.itinerary_id if a.stops_count < b.stops_count else b.itinerary_id
        bullets.append(f"{fewer} has fewer stops.")
    if not bullets:
        bullets.append("Both itineraries are similar across price, time, and restrictions.")
    return bullets
