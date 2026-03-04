"use client";

import { useMemo, useState } from "react";

import { FinalItineraryItem, FinalSearchResult, NormalizedItinerary, SearchRequest } from "@/lib/types";
import ComparePanel from "./ComparePanel";
import ItineraryCard from "./ItineraryCard";

interface Props {
  result: FinalSearchResult;
  requestSnapshot: SearchRequest | null;
}

type TabId = "cheapest" | "nonstop" | "strategic";

const TAB_META: Record<TabId, { label: string; blurb: string }> = {
  cheapest: {
    label: "Cheapest",
    blurb: "Lowest true total after baggage and fare rules",
  },
  nonstop: {
    label: "Nonstop",
    blurb: "0-stop routes ranked by true total + duration",
  },
  strategic: {
    label: "Strategic",
    blurb: "Explainable weighted score across cost, time, risk",
  },
};

function snapshotChips(request: SearchRequest | null, modeLabel: string): string[] {
  if (!request) {
    return [];
  }
  return [
    `${request.origin_airports.join("/")} → ${request.destination_query}`,
    `${request.departure_dates.length} depart date(s) • ${request.return_dates.length} return date(s)`,
    `${request.passengers_adults} traveler • ${request.cabin.replace("_", " ")}`,
    `${request.carry_on_count} carry-on • ${request.checked_bag_count} checked`,
    request.prefer_nonstop ? "Prefer nonstop" : "Nonstop optional",
    modeLabel,
  ];
}

export default function ResultsTabs({ result, requestSnapshot }: Props) {
  const [active, setActive] = useState<TabId>("cheapest");
  const [compareIds, setCompareIds] = useState<string[]>([]);
  const [compareOpen, setCompareOpen] = useState(false);

  const poolMap = useMemo(() => {
    const map = new Map<string, NormalizedItinerary>();
    result.compare_pool.forEach((item) => map.set(item.itinerary_id, item));
    return map;
  }, [result.compare_pool]);

  const activeItems: FinalItineraryItem[] = result[active] as FinalItineraryItem[];

  const tabCounts = {
    cheapest: result.cheapest.length,
    nonstop: result.nonstop.length,
    strategic: result.strategic.length,
  };

  const verifiedCount = result.compare_pool.filter((item) => item.verified).length;
  const unverifiedCount = result.compare_pool.length - verifiedCount;

  const toggleCompare = (id: string) => {
    setCompareIds((prev) => {
      if (prev.includes(id)) {
        const next = prev.filter((value) => value !== id);
        if (next.length < 2) {
          setCompareOpen(false);
        }
        return next;
      }
      if (prev.length >= 2) {
        setCompareOpen(false);
        return [prev[1], id];
      }
      return [...prev, id];
    });
  };

  const left = compareIds[0] ? poolMap.get(compareIds[0]) : undefined;
  const right = compareIds[1] ? poolMap.get(compareIds[1]) : undefined;

  const dataMode = typeof result.metadata.data_mode === "string" ? result.metadata.data_mode : "";
  const isDryRun = requestSnapshot?.dry_run ?? false;
  const modeLabel =
    dataMode === "fixtures" && isDryRun
      ? "Dry run fixtures"
      : dataMode === "fixtures"
        ? "Fixture-projected results"
        : dataMode === "live"
          ? "Live source mode"
          : isDryRun
            ? "Dry run fixtures"
            : "Source mode unknown";
  const chips = snapshotChips(requestSnapshot, modeLabel);

  return (
    <section className="space-y-4 pb-24">
      <header className="surface-card p-4">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <p className="eyebrow">Results Dashboard</p>
            <h2 className="text-2xl font-semibold text-ink">Choose your best itinerary with verified trust signals</h2>
          </div>
          <div className="flex flex-wrap items-center gap-2 text-xs">
            <span className="chip-verified">Verified {verifiedCount}</span>
            <span className="chip-muted">Unverified {unverifiedCount}</span>
            <span className="chip-muted">{result.cache_hit ? "Cache hit" : "Fresh run"}</span>
            <span className="chip-muted">Status: {result.status}</span>
          </div>
        </div>

        {chips.length > 0 ? (
          <div className="mt-3 flex flex-wrap gap-2">
            {chips.map((chip) => (
              <span key={chip} className="chip-muted">
                {chip}
              </span>
            ))}
          </div>
        ) : null}

        {result.warnings.length > 0 ? (
          <ul className="alert-card mt-3 list-disc space-y-1 pl-5 text-sm">
            {result.warnings.map((warning) => (
              <li key={warning}>{warning}</li>
            ))}
          </ul>
        ) : null}
      </header>

      <div className="sticky top-2 z-20 surface-card p-3">
        <div className="grid gap-2 md:grid-cols-3">
          {(Object.keys(TAB_META) as TabId[]).map((tab) => {
            const isActive = tab === active;
            return (
              <button
                key={tab}
                onClick={() => setActive(tab)}
                className={`tab-button ${isActive ? "tab-button-active" : "tab-button-idle"}`}
                type="button"
                aria-pressed={isActive}
              >
                <span className="text-left text-sm font-semibold">
                  {TAB_META[tab].label} <span className="text-xs">({tabCounts[tab]})</span>
                </span>
                <span className="text-left text-xs text-slate-500">{TAB_META[tab].blurb}</span>
              </button>
            );
          })}
        </div>
      </div>

      <div className="grid gap-4">
        {activeItems.map((item, index) => (
          <ItineraryCard
            key={item.itinerary.itinerary_id}
            item={item}
            mode={index === 0 ? "expanded" : "compact"}
            tabLabel={TAB_META[active].label}
            selected={compareIds.includes(item.itinerary.itinerary_id)}
            onToggleCompare={toggleCompare}
          />
        ))}
      </div>

      {left && right && compareOpen ? <ComparePanel left={left} right={right} /> : null}

      {compareIds.length > 0 ? (
        <aside className="compare-tray" aria-live="polite">
          <div>
            <p className="text-xs uppercase tracking-[0.12em] text-slate-500">Compare tray</p>
            <p className="text-sm text-slate-700">{compareIds.length} itinerary selected</p>
            <p className="text-xs text-slate-500">Pick two to unlock side-by-side comparison.</p>
          </div>
          <div className="flex flex-wrap gap-2">
            {compareIds.map((id) => (
              <button key={id} className="chip-muted" onClick={() => toggleCompare(id)} type="button">
                {id} x
              </button>
            ))}
          </div>
          <div className="flex gap-2">
            <button
              type="button"
              className="button-secondary"
              onClick={() => setCompareOpen((prev) => !prev)}
              disabled={compareIds.length < 2}
            >
              {compareOpen ? "Hide compare" : "Compare now"}
            </button>
            <button
              type="button"
              className="button-ghost"
              onClick={() => {
                setCompareIds([]);
                setCompareOpen(false);
              }}
            >
              Clear
            </button>
          </div>
        </aside>
      ) : null}
    </section>
  );
}
