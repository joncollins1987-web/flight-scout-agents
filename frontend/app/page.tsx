"use client";

import { useState } from "react";

import ResultsTabs from "@/components/ResultsTabs";
import SearchWizard from "@/components/SearchWizard";
import { searchFlights } from "@/lib/api";
import { FinalSearchResult, SearchRequest } from "@/lib/types";

export default function HomePage() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<FinalSearchResult | null>(null);
  const [submittedRequest, setSubmittedRequest] = useState<SearchRequest | null>(null);

  const handleSearch = async (payload: SearchRequest) => {
    setLoading(true);
    setError(null);
    setSubmittedRequest(payload);
    try {
      const response = await searchFlights(payload);
      setResult(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Search request failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="mx-auto flex min-h-screen max-w-7xl flex-col gap-6 px-4 py-6 md:px-6">
      <header className="surface-card p-5">
        <p className="eyebrow">flight-scout-agents</p>
        <h1 className="mt-2 text-4xl font-semibold text-ink">Multi-Agent Flight Scout</h1>
        <p className="mt-2 max-w-3xl text-sm text-slate-600">
          Finds cheapest true-total fare, best nonstop, and most strategic itinerary with verification evidence and optional stopover plans.
        </p>
      </header>

      <SearchWizard loading={loading} onSubmit={handleSearch} />

      {error ? <div className="alert-card">{error}</div> : null}
      {result ? <ResultsTabs result={result} requestSnapshot={submittedRequest} /> : null}
    </main>
  );
}
