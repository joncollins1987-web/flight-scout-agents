"use client";

import { useState } from "react";

import { ResultCardMode } from "@/lib/ui-types";
import { FinalItineraryItem } from "@/lib/types";
import { formatCurrency, formatDateTime, formatMinutes } from "@/lib/formatters";
import StopoverPanel from "./StopoverPanel";

interface Props {
  item: FinalItineraryItem;
  tabLabel: string;
  mode: ResultCardMode;
  selected: boolean;
  onToggleCompare: (id: string) => void;
}

function verifiedLabel(item: FinalItineraryItem): string {
  if (!item.itinerary.verified) {
    return "Unverified";
  }
  if (item.itinerary.verified_at) {
    return `Verified ${new Date(item.itinerary.verified_at).toLocaleString()}`;
  }
  return "Verified";
}

function isBookableUrl(url: string | null): boolean {
  if (!url || !/^https?:\/\//i.test(url)) {
    return false;
  }
  try {
    const host = new URL(url).hostname.toLowerCase();
    return !["fixtures.local", "example.com", "www.example.com"].includes(host);
  } catch {
    return false;
  }
}

function fallbackBookingUrl(item: FinalItineraryItem): string {
  const itinerary = item.itinerary;
  const origin = itinerary.origin_airport;
  const destination = itinerary.destination_airport;
  const depart = itinerary.depart_date;
  const ret = itinerary.return_date;
  const params = new URLSearchParams({
    sort: "bestflight_a",
    currency: "USD",
    adults: "1",
    cabin: "e",
  });
  return `https://www.kayak.com/flights/${origin}-${destination}/${depart}/${ret}?${params.toString()}`;
}

export default function ItineraryCard({ item, tabLabel, mode, selected, onToggleCompare }: Props) {
  const [expanded, setExpanded] = useState(mode === "expanded");
  const itinerary = item.itinerary;
  const rawBookingUrl = itinerary.booking_url ?? itinerary.verification_evidence?.checked_url ?? null;
  const bookingUrl = isBookableUrl(rawBookingUrl) ? rawBookingUrl : fallbackBookingUrl(item);
  const hasBookUrl = Boolean(bookingUrl);

  return (
    <article className={`itinerary-card ${mode === "expanded" ? "itinerary-card-emphasis" : "itinerary-card-surface"}`}>
      <header className="flex flex-wrap items-start justify-between gap-3">
        <div className="space-y-1">
          <div className="flex flex-wrap items-center gap-2">
            <span className="chip-muted">{tabLabel}</span>
            <span className={itinerary.verified ? "chip-verified" : "chip-warning"}>{verifiedLabel(item)}</span>
            <span className="chip-muted">Source {itinerary.source}</span>
          </div>
          <p className="text-xs uppercase tracking-[0.12em] text-slate-500">Itinerary {itinerary.itinerary_id}</p>
        </div>
        <button
          type="button"
          className="button-ghost"
          onClick={() => setExpanded((prev) => !prev)}
          aria-expanded={expanded}
        >
          {expanded ? "Hide details" : "Expand details"}
        </button>
      </header>

      <section className="mt-4 grid gap-3 rounded-xl border border-slate-200 bg-white p-3 md:grid-cols-4">
        <div>
          <p className="metric-label">True total</p>
          <p className="metric-value">{formatCurrency(itinerary.true_total_price_usd)}</p>
          <p className="metric-sub">Base {formatCurrency(itinerary.base_fare_usd)} + taxes {formatCurrency(itinerary.taxes_fees_usd)}</p>
        </div>
        <div>
          <p className="metric-label">Duration</p>
          <p className="metric-value">{formatMinutes(itinerary.total_travel_time_minutes)}</p>
          <p className="metric-sub">{itinerary.stops_count} stop(s)</p>
        </div>
        <div>
          <p className="metric-label">Risk profile</p>
          <p className="metric-value">{itinerary.tight_connection ? "Elevated" : "Stable"}</p>
          <p className="metric-sub">{itinerary.self_transfer ? "Self-transfer involved" : "Single-ticket flow"}</p>
        </div>
        <div>
          <p className="metric-label">Strategic score</p>
          <p className="metric-value">{itinerary.score?.total_score?.toFixed(1) ?? "N/A"}</p>
          <p className="metric-sub">Weighted cost/time/convenience/risk</p>
        </div>
      </section>

      <section className="mt-4 space-y-3 rounded-xl border border-slate-200 bg-slate-50 p-3">
        <div>
          <p className="text-sm font-semibold text-slate-700">Route timeline</p>
          <p className="text-xs text-slate-500">Outbound and inbound condensed for quick comparison.</p>
        </div>
        <div className="grid gap-3 md:grid-cols-2">
          <div className="timeline-card">
            <p className="timeline-title">Outbound</p>
            <p className="timeline-main">{itinerary.origin_airport} → {itinerary.destination_airport}</p>
            <p className="timeline-sub">
              {formatDateTime(itinerary.segments_outbound[0].departure_time_utc)}
              {" "}to{" "}
              {formatDateTime(itinerary.segments_outbound[itinerary.segments_outbound.length - 1].arrival_time_utc)}
            </p>
          </div>
          <div className="timeline-card">
            <p className="timeline-title">Inbound</p>
            <p className="timeline-main">{itinerary.destination_airport} → {itinerary.origin_airport}</p>
            <p className="timeline-sub">
              {formatDateTime(itinerary.segments_inbound[0].departure_time_utc)}
              {" "}to{" "}
              {formatDateTime(itinerary.segments_inbound[itinerary.segments_inbound.length - 1].arrival_time_utc)}
            </p>
          </div>
        </div>
      </section>

      <section className="mt-4 grid gap-2 rounded-xl border border-slate-200 bg-white p-3 text-sm md:grid-cols-2">
        <p><span className="font-semibold">Fare:</span> {itinerary.fare_brand ?? "Unknown"}</p>
        <p><span className="font-semibold">Baggage:</span> {itinerary.baggage_rules_summary ?? "Unknown"}</p>
        <p><span className="font-semibold">Seat cost:</span> {itinerary.seat_cost_summary ?? "Unknown"}</p>
        <p><span className="font-semibold">Change/cancel:</span> {itinerary.change_cancel_summary ?? "Unknown"}</p>
      </section>

      {itinerary.gotchas.length > 0 ? (
        <section className="mt-4 flex flex-wrap gap-2">
          {itinerary.gotchas.map((gotcha) => (
            <span key={gotcha} className="chip-warning">
              {gotcha}
            </span>
          ))}
        </section>
      ) : null}

      {item.why_bullets.length > 0 ? (
        <section className="mt-4 rounded-xl border border-sky-200 bg-sky-50 p-3">
          <p className="text-sm font-semibold text-sky-900">Why this itinerary ranks well</p>
          <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-sky-900">
            {item.why_bullets.map((bullet) => (
              <li key={bullet}>{bullet}</li>
            ))}
          </ul>
        </section>
      ) : null}

      {expanded ? (
        <section className="mt-4 grid gap-3 md:grid-cols-2">
          <div className="surface-card p-3 text-sm">
            <p className="font-semibold text-ink">Outbound segments</p>
            {itinerary.segments_outbound.map((segment) => (
              <p key={`${segment.flight_number}-${segment.departure_time_utc}`} className="mt-2 border-t border-slate-200 pt-2 first:mt-1 first:border-t-0 first:pt-0">
                {segment.carrier} {segment.flight_number}: {segment.origin_airport} → {segment.destination_airport} ({formatDateTime(segment.departure_time_utc)} - {formatDateTime(segment.arrival_time_utc)})
              </p>
            ))}
          </div>
          <div className="surface-card p-3 text-sm">
            <p className="font-semibold text-ink">Inbound segments</p>
            {itinerary.segments_inbound.map((segment) => (
              <p key={`${segment.flight_number}-${segment.departure_time_utc}`} className="mt-2 border-t border-slate-200 pt-2 first:mt-1 first:border-t-0 first:pt-0">
                {segment.carrier} {segment.flight_number}: {segment.origin_airport} → {segment.destination_airport} ({formatDateTime(segment.departure_time_utc)} - {formatDateTime(segment.arrival_time_utc)})
              </p>
            ))}
          </div>
        </section>
      ) : null}

      {item.stopover_plan ? <div className="mt-4"><StopoverPanel plan={item.stopover_plan} /></div> : null}

      <footer className="mt-4 flex items-center justify-between gap-3 border-t border-slate-200 pt-3">
        <div className="text-xs text-slate-500">
          <p>Compare to keep this itinerary in side-by-side mode.</p>
          <p>Book opens the source page with itinerary query parameters when available.</p>
        </div>
        <div className="flex flex-wrap gap-2">
          {hasBookUrl ? (
            <a className="button-secondary" href={bookingUrl ?? undefined} target="_blank" rel="noopener noreferrer">
              Book this flight
            </a>
          ) : (
            <button type="button" className="button-ghost" disabled title="This run used fixture/stub data and has no real booking deep link.">
              Real booking link unavailable
            </button>
          )}
          <button
            className={selected ? "button-secondary" : "button-ghost"}
            onClick={() => onToggleCompare(itinerary.itinerary_id)}
            type="button"
          >
            {selected ? "Selected for compare" : "Add to compare"}
          </button>
        </div>
      </footer>
    </article>
  );
}
