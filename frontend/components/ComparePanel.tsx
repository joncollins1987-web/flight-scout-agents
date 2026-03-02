import { NormalizedItinerary } from "@/lib/types";
import { compareItinerariesGrouped } from "@/lib/utils";
import { formatCurrency, formatMinutes } from "@/lib/formatters";

interface Props {
  left: NormalizedItinerary;
  right: NormalizedItinerary;
}

function Section({ title, bullets }: { title: string; bullets: string[] }) {
  return (
    <section className="surface-card p-3">
      <h4 className="text-sm font-semibold text-ink">{title}</h4>
      <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-slate-700">
        {bullets.map((bullet) => (
          <li key={bullet}>{bullet}</li>
        ))}
      </ul>
    </section>
  );
}

export default function ComparePanel({ left, right }: Props) {
  const grouped = compareItinerariesGrouped(left, right);

  return (
    <div className="surface-card p-4">
      <h3 className="text-lg font-semibold text-ink">Side-by-side comparison</h3>
      <p className="mt-1 text-sm text-slate-600">{left.itinerary_id} vs {right.itinerary_id}</p>

      <div className="mt-4 grid gap-3 lg:grid-cols-2">
        <div className="emphasis-card p-3 text-sm">
          <p className="font-semibold text-ink">{left.itinerary_id}</p>
          <p>{formatCurrency(left.true_total_price_usd)} • {formatMinutes(left.total_travel_time_minutes)} • {left.stops_count} stop(s)</p>
        </div>
        <div className="emphasis-card p-3 text-sm">
          <p className="font-semibold text-ink">{right.itinerary_id}</p>
          <p>{formatCurrency(right.true_total_price_usd)} • {formatMinutes(right.total_travel_time_minutes)} • {right.stops_count} stop(s)</p>
        </div>
      </div>

      <div className="mt-4 grid gap-3 lg:grid-cols-3">
        <Section title="Price" bullets={grouped.price} />
        <Section title="Time" bullets={grouped.time} />
        <Section title="Restrictions" bullets={grouped.restrictions} />
      </div>
    </div>
  );
}
