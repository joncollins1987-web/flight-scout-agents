import { FinalSearchResult, SearchRequest } from "./types";

const BACKEND = process.env.NEXT_PUBLIC_BACKEND_URL ?? "http://localhost:8000";

export async function searchFlights(payload: SearchRequest): Promise<FinalSearchResult> {
  const response = await fetch(`${BACKEND}/api/search`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const message = await response.text();
    throw new Error(`Search failed (${response.status}): ${message}`);
  }

  return (await response.json()) as FinalSearchResult;
}
