import { Cabin, SearchRequest, StopoverEffort } from "./types";

export type WizardStepId =
  | "route_travelers"
  | "date_flex"
  | "price_fare"
  | "comfort_stops"
  | "stopover_engine";

export type ResultCardMode = "compact" | "expanded";

export interface MonthBucket {
  monthKey: string;
  monthLabel: string;
  dates: string[];
}

export interface SearchDraft {
  originAirports: string[];
  includeNearbyAirports: boolean;
  nearbyRadiusMiles: number | "";
  destinationQuery: string;
  departureDates: string[];
  returnDates: string[];
  passengersAdults: number;
  cabin: Cabin;
  carryOnCount: number;
  checkedBagCount: number;
  basicEconomyAllowed: boolean;
  refundableRequired: boolean;
  targetBudgetUsd: number | "";
  earliestDepartLocal: string;
  latestArriveLocal: string;
  allowStopovers: boolean;
  maxLayoverMinutes: number | "";
  preferNonstop: boolean;
  stopoverPlanEnabled: boolean;
  stopoverBudgetUsd: number | "";
  stopoverEffort: StopoverEffort;
  stopoverLeaveAirport: boolean;
  avoidRedEyes: boolean;
  avoidTightConnections: boolean;
  preferredAirlines: string;
  blockedAirlines: string;
  dryRun: boolean;
  maxVerifyPerTab: number;
  sourceFlags: {
    aggregator_one: boolean;
    aggregator_two: boolean;
  };
}

export interface SearchSummaryItem {
  id: string;
  section: "Trip" | "Dates" | "Fare" | "Comfort" | "Engine";
  label: string;
  value: string;
  tone?: "neutral" | "good" | "warning";
}

export interface WizardStepDefinition {
  id: WizardStepId;
  title: string;
  description: string;
}

export interface StepValidationResult {
  valid: boolean;
  errors: string[];
}

export interface SearchWizardProps {
  loading: boolean;
  onSubmit: (payload: SearchRequest) => Promise<void>;
}
