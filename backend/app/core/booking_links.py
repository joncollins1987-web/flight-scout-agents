from __future__ import annotations

from datetime import date
from urllib.parse import urlencode, urlparse


PLACEHOLDER_HOSTS = {"fixtures.local", "example.com", "www.example.com"}

_CABIN_MAP = {
    "economy": "e",
    "premium_economy": "p",
    "business": "b",
    "first": "f",
}


def is_placeholder_booking_url(url: str | None) -> bool:
    if not url:
        return True
    parsed = urlparse(url)
    host = (parsed.netloc or "").lower()
    if not host:
        return True
    return host in PLACEHOLDER_HOSTS


def build_kayak_search_url(
    origin: str,
    destination: str,
    depart_date: date,
    return_date: date,
    adults: int = 1,
    cabin: str = "economy",
    currency: str = "USD",
) -> str:
    cabin_code = _CABIN_MAP.get(cabin, "e")
    path = f"/flights/{origin}-{destination}/{depart_date.isoformat()}/{return_date.isoformat()}"
    query = urlencode(
        {
            "sort": "bestflight_a",
            "currency": currency,
            "adults": adults,
            "cabin": cabin_code,
        }
    )
    return f"https://www.kayak.com{path}?{query}"


def ensure_actionable_booking_url(
    url: str | None,
    *,
    origin: str,
    destination: str,
    depart_date: date,
    return_date: date,
    adults: int = 1,
    cabin: str = "economy",
    currency: str = "USD",
) -> str:
    if not is_placeholder_booking_url(url):
        return url or ""
    return build_kayak_search_url(
        origin=origin,
        destination=destination,
        depart_date=depart_date,
        return_date=return_date,
        adults=adults,
        cabin=cabin,
        currency=currency,
    )
