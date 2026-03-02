export type Cabin = "economy" | "premium_economy" | "business" | "first";
export type StopoverEffort = "low" | "medium" | "high";

export interface SearchRequest {
  origin_airports: string[];
  include_nearby_airports: boolean;
  nearby_airports: string[];
  nearby_radius_miles?: number | null;
  destination_query: string;
  departure_dates: string[];
  return_dates: string[];
  passengers_adults: number;
  cabin: Cabin;
  currency: "USD";
  carry_on_count: number;
  checked_bag_count: number;
  basic_economy_allowed: boolean;
  refundable_required: boolean;
  earliest_depart_local?: string | null;
  latest_arrive_local?: string | null;
  allow_stopovers: boolean;
  max_layover_minutes?: number | null;
  prefer_nonstop: boolean;
  stopover_plan_enabled: boolean;
  stopover_budget_usd?: number | null;
  stopover_effort: StopoverEffort;
  stopover_leave_airport: boolean;
  avoid_red_eyes: boolean;
  avoid_tight_connections: boolean;
  preferred_airlines: string[];
  blocked_airlines: string[];
  dry_run: boolean;
  max_verify_per_tab: number;
  source_flags: Record<string, boolean>;
}

export interface ScoreBreakdown {
  itinerary_id: string;
  total_price_true: number;
  total_travel_time_minutes: number;
  convenience_vs_windows: number;
  connection_risk: number;
  red_eye_penalty: number;
  total_score: number;
  why_bullets: string[];
}

export interface VerificationEvidence {
  verified_at: string;
  checked_url: string;
  price_text_snapshot: string;
  fare_brand_text?: string | null;
  baggage_rules_text?: string | null;
  seat_fee_text?: string | null;
  change_cancel_text?: string | null;
  screenshot_path?: string | null;
}

export interface FlightSegment {
  carrier: string;
  flight_number: string;
  origin_airport: string;
  destination_airport: string;
  departure_time_utc: string;
  arrival_time_utc: string;
  duration_minutes: number;
  origin_terminal?: string | null;
  destination_terminal?: string | null;
}

export interface NormalizedItinerary {
  itinerary_id: string;
  source: string;
  source_candidate_ids: string[];
  booking_url?: string | null;
  origin_airport: string;
  destination_airport: string;
  depart_date: string;
  return_date: string;
  segments_outbound: FlightSegment[];
  segments_inbound: FlightSegment[];
  base_fare_usd: number;
  taxes_fees_usd: number;
  estimated_true_total_usd: number;
  true_total_price_usd: number;
  fare_brand?: string | null;
  refundable: boolean;
  baggage_rules_summary?: string | null;
  seat_cost_summary?: string | null;
  change_cancel_summary?: string | null;
  stops_count: number;
  total_travel_time_minutes: number;
  longest_layover_minutes?: number | null;
  self_transfer: boolean;
  tight_connection: boolean;
  red_eye: boolean;
  gotchas: string[];
  policy_flags: Record<string, boolean>;
  verified: boolean;
  verified_at?: string | null;
  verified_total_price_usd?: number | null;
  verification_status: string;
  verification_material_change: boolean;
  verification_evidence?: VerificationEvidence | null;
  score?: ScoreBreakdown | null;
}

export interface StopoverPlan {
  itinerary_id: string;
  layover_airport: string;
  usable_time_minutes: number;
  transit_time_minutes_est: number;
  transit_cost_usd_est: number;
  budget_fit?: boolean | null;
  bullets: string[];
  warnings: string[];
}

export interface FinalItineraryItem {
  itinerary: NormalizedItinerary;
  why_bullets: string[];
  stopover_plan?: StopoverPlan | null;
}

export interface FinalSearchResult {
  run_id: string;
  generated_at: string;
  status: "ok" | "partial" | "warning";
  cache_hit: boolean;
  cache_expires_at?: string | null;
  warnings: string[];
  cheapest: FinalItineraryItem[];
  nonstop: FinalItineraryItem[];
  strategic: FinalItineraryItem[];
  compare_pool: NormalizedItinerary[];
  metadata: Record<string, string | number | boolean | null>;
}
