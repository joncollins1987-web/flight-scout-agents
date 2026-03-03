from __future__ import annotations

from datetime import date

from app.core.booking_links import ensure_actionable_booking_url, is_placeholder_booking_url


def test_placeholder_url_gets_replaced_with_actionable_link() -> None:
    url = ensure_actionable_booking_url(
        "https://example.com/placeholder",
        origin="JFK",
        destination="TLV",
        depart_date=date(2026, 4, 10),
        return_date=date(2026, 4, 18),
        adults=1,
        cabin="economy",
        currency="USD",
    )
    assert url.startswith("https://www.kayak.com/flights/JFK-TLV/2026-04-10/2026-04-18")
    assert not is_placeholder_booking_url(url)


def test_real_url_is_preserved() -> None:
    real_url = "https://www.kayak.com/flights/JFK-TLV/2026-04-10/2026-04-18"
    url = ensure_actionable_booking_url(
        real_url,
        origin="JFK",
        destination="TLV",
        depart_date=date(2026, 4, 10),
        return_date=date(2026, 4, 18),
    )
    assert url == real_url
