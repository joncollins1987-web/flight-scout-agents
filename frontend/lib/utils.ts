import { formatCurrency, formatDateTime, formatMinutes } from "./formatters";
import { NormalizedItinerary } from "./types";

export function compareItineraries(a: NormalizedItinerary, b: NormalizedItinerary): string[] {
  const bullets: string[] = [];

  const priceDiff = a.true_total_price_usd - b.true_total_price_usd;
  if (priceDiff !== 0) {
    const winner = priceDiff < 0 ? a.itinerary_id : b.itinerary_id;
    bullets.push(`${winner} is $${Math.abs(priceDiff).toFixed(2)} cheaper (true total).`);
  }

  const timeDiff = Math.abs(a.total_travel_time_minutes - b.total_travel_time_minutes);
  if (timeDiff > 0) {
    const faster = a.total_travel_time_minutes < b.total_travel_time_minutes ? a.itinerary_id : b.itinerary_id;
    bullets.push(`${faster} is ${timeDiff} minutes faster total travel time.`);
  }

  if (a.refundable !== b.refundable) {
    const refundable = a.refundable ? a.itinerary_id : b.itinerary_id;
    bullets.push(`${refundable} has a refundable fare.`);
  }

  if (a.stops_count !== b.stops_count) {
    const fewerStops = a.stops_count < b.stops_count ? a.itinerary_id : b.itinerary_id;
    bullets.push(`${fewerStops} has fewer stops.`);
  }

  return bullets.length ? bullets : ["No significant differences across price/time/restrictions."];
}

export interface CompareGroups {
  price: string[];
  time: string[];
  restrictions: string[];
}

export function compareItinerariesGrouped(a: NormalizedItinerary, b: NormalizedItinerary): CompareGroups {
  const price: string[] = [];
  const time: string[] = [];
  const restrictions: string[] = [];

  const priceDiff = a.true_total_price_usd - b.true_total_price_usd;
  if (priceDiff !== 0) {
    const winner = priceDiff < 0 ? a.itinerary_id : b.itinerary_id;
    price.push(`${winner} is ${formatCurrency(Math.abs(priceDiff))} cheaper on true total.`);
  } else {
    price.push("Both itineraries are equal on true total price.");
  }

  const durationDiff = Math.abs(a.total_travel_time_minutes - b.total_travel_time_minutes);
  if (durationDiff > 0) {
    const faster = a.total_travel_time_minutes < b.total_travel_time_minutes ? a.itinerary_id : b.itinerary_id;
    time.push(`${faster} is ${formatMinutes(durationDiff)} faster end-to-end.`);
  } else {
    time.push("Both itineraries have the same total travel time.");
  }

  if (a.stops_count !== b.stops_count) {
    const fewerStops = a.stops_count < b.stops_count ? a.itinerary_id : b.itinerary_id;
    restrictions.push(`${fewerStops} has fewer stops.`);
  }
  if (a.refundable !== b.refundable) {
    const refundable = a.refundable ? a.itinerary_id : b.itinerary_id;
    restrictions.push(`${refundable} is refundable.`);
  }
  if (a.self_transfer !== b.self_transfer) {
    const safer = a.self_transfer ? b.itinerary_id : a.itinerary_id;
    restrictions.push(`${safer} avoids self-transfer complexity.`);
  }
  if (!restrictions.length) {
    restrictions.push("Restrictions and risk profile are similar.");
  }

  return { price, time, restrictions };
}

export { formatCurrency, formatDateTime, formatMinutes };
