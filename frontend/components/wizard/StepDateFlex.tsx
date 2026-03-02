import { NEARBY_ORIGINS } from "@/lib/wizard";
import { DateStepProps } from "./types";
import MonthScroller from "./MonthScroller";

function toggleValue(values: string[], value: string): string[] {
  if (values.includes(value)) {
    return values.filter((item) => item !== value);
  }
  return [...values, value];
}

export default function StepDateFlex({ draft, updateDraft, monthBuckets }: DateStepProps) {
  return (
    <section className="space-y-6" aria-labelledby="step-date-flex">
      <div>
        <h3 id="step-date-flex" className="text-2xl font-semibold text-ink">
          Date Flexibility
        </h3>
        <p className="text-sm text-slate-600">
          Use the month dropdown to switch calendars and select far-ahead departure/return windows.
        </p>
      </div>

      <fieldset className="surface-card space-y-3 p-4">
        <legend className="text-sm font-semibold text-slate-700">Nearby airport behavior</legend>
        <label className="inline-flex items-center gap-2 text-sm">
          <input
            type="checkbox"
            checked={draft.includeNearbyAirports}
            onChange={(event) => updateDraft({ includeNearbyAirports: event.target.checked })}
          />
          Include nearby airports ({NEARBY_ORIGINS.join(" / ")})
        </label>
        {draft.includeNearbyAirports ? (
          <label className="input-group max-w-xs">
            <span>Radius miles</span>
            <input
              type="number"
              min={1}
              max={300}
              value={draft.nearbyRadiusMiles}
              onChange={(event) =>
                updateDraft({ nearbyRadiusMiles: event.target.value === "" ? "" : Number(event.target.value) })
              }
            />
          </label>
        ) : null}
      </fieldset>

      <div className="grid gap-4">
        <MonthScroller
          legend="Departure dates"
          description="Choose all departure dates you would accept."
          prefix="depart"
          monthBuckets={monthBuckets}
          selectedDates={draft.departureDates}
          onToggleDate={(date) =>
            updateDraft({ departureDates: toggleValue(draft.departureDates, date) })
          }
        />

        <MonthScroller
          legend="Return dates"
          description="Choose acceptable return dates."
          prefix="return"
          monthBuckets={monthBuckets}
          selectedDates={draft.returnDates}
          onToggleDate={(date) =>
            updateDraft({ returnDates: toggleValue(draft.returnDates, date) })
          }
        />
      </div>
    </section>
  );
}
