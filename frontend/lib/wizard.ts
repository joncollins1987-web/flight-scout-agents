import { formatDate, formatMonthLabel, listSummary, readableTime } from "./formatters";
import { SearchRequest } from "./types";
import {
  MonthBucket,
  SearchDraft,
  SearchSummaryItem,
  StepValidationResult,
  WizardStepDefinition,
  WizardStepId,
} from "./ui-types";

export const PRIMARY_ORIGINS = ["JFK", "EWR", "LGA"];
export const NEARBY_ORIGINS = ["HPN", "ISP", "PHL"];
export const DATE_HORIZON_MONTHS = 18;

export const WIZARD_STEPS: WizardStepDefinition[] = [
  {
    id: "route_travelers",
    title: "Route & Travelers",
    description: "Where you are flying and who is traveling.",
  },
  {
    id: "date_flex",
    title: "Date Flexibility",
    description: "Select acceptable departure and return windows.",
  },
  {
    id: "price_fare",
    title: "Price & Fare Rules",
    description: "Set baggage and fare restrictions for true-cost ranking.",
  },
  {
    id: "comfort_stops",
    title: "Comfort & Stops",
    description: "Tune stop, layover, and timing preferences.",
  },
  {
    id: "stopover_engine",
    title: "Stopover + Engine",
    description: "Stopover planning and advanced run controls.",
  },
];

function toIsoDate(year: number, monthIndex: number, day: number): string {
  const month = String(monthIndex + 1).padStart(2, "0");
  const normalizedDay = String(day).padStart(2, "0");
  return `${year}-${month}-${normalizedDay}`;
}

function startOfDay(value: Date): Date {
  return new Date(value.getFullYear(), value.getMonth(), value.getDate());
}

export function buildMonthBuckets(monthCount = DATE_HORIZON_MONTHS, fromDate = new Date()): MonthBucket[] {
  const today = startOfDay(fromDate);
  const startMonth = new Date(today.getFullYear(), today.getMonth(), 1);
  const buckets: MonthBucket[] = [];

  for (let offset = 0; offset < monthCount; offset += 1) {
    const monthDate = new Date(startMonth.getFullYear(), startMonth.getMonth() + offset, 1);
    const monthKey = toIsoDate(monthDate.getFullYear(), monthDate.getMonth(), 1).slice(0, 7);
    const daysInMonth = new Date(monthDate.getFullYear(), monthDate.getMonth() + 1, 0).getDate();

    const dates: string[] = [];
    for (let day = 1; day <= daysInMonth; day += 1) {
      const candidate = new Date(monthDate.getFullYear(), monthDate.getMonth(), day);
      if (candidate < today) {
        continue;
      }
      dates.push(toIsoDate(monthDate.getFullYear(), monthDate.getMonth(), day));
    }

    if (dates.length) {
      buckets.push({
        monthKey,
        monthLabel: formatMonthLabel(monthKey),
        dates,
      });
    }
  }

  return buckets;
}

export function flattenMonthDates(monthBuckets: MonthBucket[]): string[] {
  return monthBuckets.flatMap((bucket) => bucket.dates);
}

export function createDefaultDraft(monthBuckets: MonthBucket[]): SearchDraft {
  const allDates = flattenMonthDates(monthBuckets);
  const fallbackDeparture = allDates.slice(0, 1);
  const fallbackReturn = allDates.slice(1, 2);

  const departureDates = allDates.slice(0, 2).length ? allDates.slice(0, 2) : fallbackDeparture;
  const returnDates = allDates.slice(6, 8).length
    ? allDates.slice(6, 8)
    : allDates.slice(2, 4).length
      ? allDates.slice(2, 4)
      : fallbackReturn;

  return {
    originAirports: [...PRIMARY_ORIGINS],
    includeNearbyAirports: false,
    nearbyRadiusMiles: 60,
    destinationQuery: "",
    departureDates,
    returnDates,
    passengersAdults: 1,
    cabin: "economy",
    carryOnCount: 0,
    checkedBagCount: 0,
    basicEconomyAllowed: true,
    refundableRequired: false,
    targetBudgetUsd: "",
    earliestDepartLocal: "",
    latestArriveLocal: "",
    allowStopovers: true,
    maxLayoverMinutes: "",
    preferNonstop: true,
    stopoverPlanEnabled: true,
    stopoverBudgetUsd: 75,
    stopoverEffort: "medium",
    stopoverLeaveAirport: true,
    avoidRedEyes: true,
    avoidTightConnections: true,
    preferredAirlines: "",
    blockedAirlines: "",
    dryRun: false,
    maxVerifyPerTab: 5,
    sourceFlags: {
      aggregator_one: true,
      aggregator_two: true,
    },
  };
}

export function parseCodes(raw: string): string[] {
  return raw
    .split(",")
    .map((value) => value.trim().toUpperCase())
    .filter(Boolean);
}

export function buildRequestFromDraft(draft: SearchDraft): SearchRequest {
  return {
    origin_airports: draft.originAirports,
    include_nearby_airports: draft.includeNearbyAirports,
    nearby_airports: NEARBY_ORIGINS,
    nearby_radius_miles: draft.includeNearbyAirports && draft.nearbyRadiusMiles !== "" ? draft.nearbyRadiusMiles : null,
    destination_query: draft.destinationQuery.trim().toUpperCase(),
    departure_dates: draft.departureDates,
    return_dates: draft.returnDates,
    passengers_adults: draft.passengersAdults,
    cabin: draft.cabin,
    currency: "USD",
    carry_on_count: draft.carryOnCount,
    checked_bag_count: draft.checkedBagCount,
    basic_economy_allowed: draft.basicEconomyAllowed,
    refundable_required: draft.refundableRequired,
    earliest_depart_local: draft.earliestDepartLocal ? `${draft.earliestDepartLocal}:00` : null,
    latest_arrive_local: draft.latestArriveLocal ? `${draft.latestArriveLocal}:00` : null,
    allow_stopovers: draft.allowStopovers,
    max_layover_minutes: draft.maxLayoverMinutes === "" ? null : draft.maxLayoverMinutes,
    prefer_nonstop: draft.preferNonstop,
    stopover_plan_enabled: draft.stopoverPlanEnabled,
    stopover_budget_usd: draft.stopoverBudgetUsd === "" ? null : draft.stopoverBudgetUsd,
    stopover_effort: draft.stopoverEffort,
    stopover_leave_airport: draft.stopoverLeaveAirport,
    avoid_red_eyes: draft.avoidRedEyes,
    avoid_tight_connections: draft.avoidTightConnections,
    preferred_airlines: parseCodes(draft.preferredAirlines),
    blocked_airlines: parseCodes(draft.blockedAirlines),
    dry_run: draft.dryRun,
    max_verify_per_tab: draft.maxVerifyPerTab,
    source_flags: draft.sourceFlags,
  };
}

export function validateStep(
  stepId: WizardStepId,
  draft: SearchDraft,
  validDateSet?: Set<string>,
): StepValidationResult {
  const errors: string[] = [];

  if (stepId === "route_travelers") {
    if (!draft.originAirports.length) {
      errors.push("Choose at least one origin airport.");
    }
    if (draft.destinationQuery.trim().length < 3) {
      errors.push("Enter a destination city or airport code.");
    }
    if (draft.passengersAdults < 1) {
      errors.push("Passengers must be at least 1.");
    }
  }

  if (stepId === "date_flex") {
    if (!draft.departureDates.length) {
      errors.push("Select at least one departure date.");
    }
    if (!draft.returnDates.length) {
      errors.push("Select at least one return date.");
    }
    if (draft.departureDates.length && draft.returnDates.length) {
      const minDepart = draft.departureDates.slice().sort()[0];
      const minReturn = draft.returnDates.slice().sort()[0];
      if (minReturn < minDepart) {
        errors.push("Return dates must be on or after departure dates.");
      }
    }
    if (validDateSet) {
      const invalidDepart = draft.departureDates.some((date) => !validDateSet.has(date));
      const invalidReturn = draft.returnDates.some((date) => !validDateSet.has(date));
      if (invalidDepart || invalidReturn) {
        errors.push("One or more selected dates are outside the booking horizon.");
      }
    }
    if (draft.includeNearbyAirports && draft.nearbyRadiusMiles !== "" && draft.nearbyRadiusMiles < 1) {
      errors.push("Nearby radius must be at least 1 mile.");
    }
  }

  if (stepId === "price_fare") {
    if (draft.carryOnCount < 0 || draft.checkedBagCount < 0) {
      errors.push("Bag counts cannot be negative.");
    }
    if (draft.targetBudgetUsd !== "" && draft.targetBudgetUsd < 0) {
      errors.push("Budget intent must be zero or greater.");
    }
  }

  if (stepId === "comfort_stops") {
    if (draft.maxLayoverMinutes !== "" && draft.maxLayoverMinutes < 30) {
      errors.push("Max layover minutes must be at least 30.");
    }
    if (draft.allowStopovers === false && draft.preferNonstop === false) {
      errors.push("If stopovers are disabled, turn on nonstop preference.");
    }
  }

  if (stepId === "stopover_engine") {
    if (draft.maxVerifyPerTab < 3) {
      errors.push("Verify top N per tab must be at least 3.");
    }
    if (!draft.sourceFlags.aggregator_one && !draft.sourceFlags.aggregator_two) {
      errors.push("Enable at least one source module.");
    }
    if (draft.stopoverPlanEnabled && draft.stopoverBudgetUsd !== "" && draft.stopoverBudgetUsd < 0) {
      errors.push("Stopover budget must be zero or greater.");
    }
  }

  return {
    valid: errors.length === 0,
    errors,
  };
}

export function buildTripBrief(draft: SearchDraft): SearchSummaryItem[] {
  return [
    {
      id: "trip-route",
      section: "Trip",
      label: "Route",
      value: `${listSummary(draft.originAirports, "No origin")} -> ${draft.destinationQuery.trim() || "No destination"}`,
    },
    {
      id: "trip-passengers",
      section: "Trip",
      label: "Travelers",
      value: `${draft.passengersAdults} adult${draft.passengersAdults > 1 ? "s" : ""}, ${draft.cabin.replace("_", " ")}`,
    },
    {
      id: "date-window",
      section: "Dates",
      label: "Departure window",
      value: draft.departureDates.length ? draft.departureDates.slice(0, 3).map(formatDate).join(" • ") : "Not set",
    },
    {
      id: "date-return",
      section: "Dates",
      label: "Return window",
      value: draft.returnDates.length ? draft.returnDates.slice(0, 3).map(formatDate).join(" • ") : "Not set",
    },
    {
      id: "fare-bags",
      section: "Fare",
      label: "Baggage",
      value: `${draft.carryOnCount} carry-on, ${draft.checkedBagCount} checked`,
    },
    {
      id: "fare-rules",
      section: "Fare",
      label: "Fare constraints",
      value: `${draft.basicEconomyAllowed ? "Basic allowed" : "No basic"} • ${draft.refundableRequired ? "Refundable only" : "Refundable optional"}`,
      tone: draft.refundableRequired ? "good" : "neutral",
    },
    {
      id: "comfort-time",
      section: "Comfort",
      label: "Time windows",
      value: `${readableTime(draft.earliestDepartLocal)} depart • ${readableTime(draft.latestArriveLocal)} arrive`,
    },
    {
      id: "comfort-stops",
      section: "Comfort",
      label: "Stops",
      value: `${draft.allowStopovers ? "Stopovers allowed" : "Stopovers blocked"} • ${draft.preferNonstop ? "Prefer nonstop" : "Nonstop optional"}`,
    },
    {
      id: "engine-runtime",
      section: "Engine",
      label: "Run mode",
      value: `${draft.dryRun ? "Dry run fixtures" : "Live source mode"} • Verify top ${draft.maxVerifyPerTab}`,
      tone: draft.dryRun ? "neutral" : "warning",
    },
    {
      id: "engine-sources",
      section: "Engine",
      label: "Sources",
      value: `${draft.sourceFlags.aggregator_one ? "Aggregator 1" : "No A1"} • ${draft.sourceFlags.aggregator_two ? "Aggregator 2" : "No A2"}`,
      tone: !draft.sourceFlags.aggregator_one && !draft.sourceFlags.aggregator_two ? "warning" : "good",
    },
  ];
}
