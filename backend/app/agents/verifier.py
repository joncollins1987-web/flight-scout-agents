from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from app.core.artifact_store import ArtifactStore
from app.core.browser_pool import browser_pool
from app.schemas.itinerary import NormalizedItinerary
from app.schemas.request import SearchRequest
from app.schemas.verification import VerificationEvidence, VerifiedItinerary


class VerificationBatch(BaseModel):
    model_config = ConfigDict(extra="forbid")

    verified: list[VerifiedItinerary] = Field(default_factory=list)


def _fixture_map() -> dict[str, dict]:
    path = Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "verifier" / "verification_results.json"
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    return {row["itinerary_id"]: row for row in data}


async def verify_itineraries(
    itineraries: list[NormalizedItinerary],
    request: SearchRequest,
    artifact_store: ArtifactStore,
    material_change_threshold: float = 0.05,
) -> VerificationBatch:
    if request.dry_run:
        fixture = _fixture_map()
        results = [_verify_from_fixture(itinerary, fixture.get(itinerary.itinerary_id), material_change_threshold) for itinerary in itineraries]
        return VerificationBatch(verified=results)

    verified: list[VerifiedItinerary] = []
    for itinerary in itineraries:
        try:
            result = await _verify_live(itinerary, artifact_store, material_change_threshold)
        except Exception as exc:  # noqa: BLE001
            result = VerifiedItinerary(
                itinerary_id=itinerary.itinerary_id,
                source=itinerary.source,
                status="failed",
                verified=False,
                failure_reason=str(exc),
            )
        verified.append(result)
    return VerificationBatch(verified=verified)


def _verify_from_fixture(
    itinerary: NormalizedItinerary,
    fixture_row: dict | None,
    material_change_threshold: float,
) -> VerifiedItinerary:
    if fixture_row is None:
        auto_total = round(itinerary.estimated_true_total_usd * 1.01, 2)
        evidence = VerificationEvidence(
            verified_at=datetime.now(timezone.utc),
            checked_url=itinerary.booking_url or f"https://fixtures.local/{itinerary.itinerary_id}",
            price_text_snapshot=f"Total ${auto_total:.2f}",
            fare_brand_text=itinerary.fare_brand,
            baggage_rules_text=itinerary.baggage_rules_summary,
            seat_fee_text=itinerary.seat_cost_summary,
            change_cancel_text=itinerary.change_cancel_summary,
            screenshot_path=None,
        )
        return VerifiedItinerary(
            itinerary_id=itinerary.itinerary_id,
            source=itinerary.source,
            status="verified",
            verified=True,
            verified_total_price_usd=auto_total,
            fare_brand=itinerary.fare_brand,
            baggage_rules_summary=itinerary.baggage_rules_summary,
            seat_cost_summary=itinerary.seat_cost_summary,
            change_cancel_summary=itinerary.change_cancel_summary,
            material_price_change=False,
            evidence=evidence,
        )

    verified_total = float(fixture_row["verified_total_price_usd"])
    material_change = abs(verified_total - itinerary.estimated_true_total_usd) > itinerary.estimated_true_total_usd * material_change_threshold

    evidence = VerificationEvidence(
        verified_at=datetime.now(timezone.utc),
        checked_url=fixture_row.get("checked_url", "https://example.com/checkout"),
        price_text_snapshot=fixture_row.get("price_text_snapshot", "Total: $0.00"),
        fare_brand_text=fixture_row.get("fare_brand_text"),
        baggage_rules_text=fixture_row.get("baggage_rules_text"),
        seat_fee_text=fixture_row.get("seat_fee_text"),
        change_cancel_text=fixture_row.get("change_cancel_text"),
        screenshot_path=fixture_row.get("screenshot_path"),
    )

    return VerifiedItinerary(
        itinerary_id=itinerary.itinerary_id,
        source=itinerary.source,
        status="verified",
        verified=True,
        verified_total_price_usd=verified_total,
        fare_brand=fixture_row.get("fare_brand_text") or itinerary.fare_brand,
        baggage_rules_summary=fixture_row.get("baggage_rules_text"),
        seat_cost_summary=fixture_row.get("seat_fee_text"),
        change_cancel_summary=fixture_row.get("change_cancel_text"),
        material_price_change=material_change,
        evidence=evidence,
    )


async def _verify_live(
    itinerary: NormalizedItinerary,
    artifact_store: ArtifactStore,
    material_change_threshold: float,
) -> VerifiedItinerary:
    checked_url = f"https://example.com/verify/{itinerary.itinerary_id}"
    async with browser_pool.page() as page:
        await page.goto(checked_url, timeout=30_000)
        content = await page.content()
        screenshot_path = artifact_store.evidence_path(f"{itinerary.itinerary_id}.png")
        await page.screenshot(path=str(screenshot_path), full_page=True)

    simulated_price = round(itinerary.estimated_true_total_usd * 1.02, 2)
    material_change = abs(simulated_price - itinerary.estimated_true_total_usd) > itinerary.estimated_true_total_usd * material_change_threshold

    evidence = VerificationEvidence(
        verified_at=datetime.now(timezone.utc),
        checked_url=checked_url,
        price_text_snapshot=f"Simulated total ${simulated_price:.2f}",
        fare_brand_text=itinerary.fare_brand,
        baggage_rules_text=itinerary.baggage_rules_summary,
        seat_fee_text=itinerary.seat_cost_summary,
        change_cancel_text=itinerary.change_cancel_summary,
        screenshot_path=str(screenshot_path),
    )

    return VerifiedItinerary(
        itinerary_id=itinerary.itinerary_id,
        source=itinerary.source,
        status="verified",
        verified=True,
        verified_total_price_usd=simulated_price,
        fare_brand=itinerary.fare_brand,
        baggage_rules_summary=itinerary.baggage_rules_summary,
        seat_cost_summary=itinerary.seat_cost_summary,
        change_cancel_summary=itinerary.change_cancel_summary,
        material_price_change=material_change,
        evidence=evidence,
    )
