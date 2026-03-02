import { StepProps } from "./types";
import { PRIMARY_ORIGINS } from "@/lib/wizard";
import { Cabin } from "@/lib/types";

function toggleValue(values: string[], value: string): string[] {
  if (values.includes(value)) {
    return values.filter((item) => item !== value);
  }
  return [...values, value];
}

export default function StepRouteTravelers({ draft, updateDraft }: StepProps) {
  return (
    <section className="space-y-6" aria-labelledby="step-route-travelers">
      <div>
        <h3 id="step-route-travelers" className="text-2xl font-semibold text-ink">
          Route & Travelers
        </h3>
        <p className="text-sm text-slate-600">Start with the core trip details. Advanced controls come later.</p>
      </div>

      <fieldset className="surface-card space-y-3 p-4">
        <legend className="text-sm font-semibold text-slate-700">Origin airports</legend>
        <p className="text-xs text-slate-500">Choose one or more NYC airports.</p>
        <div className="flex flex-wrap gap-2 pt-1">
          {PRIMARY_ORIGINS.map((code) => (
            <label key={code} className="chip-option">
              <input
                type="checkbox"
                checked={draft.originAirports.includes(code)}
                onChange={() => updateDraft({ originAirports: toggleValue(draft.originAirports, code) })}
              />
              <span>{code}</span>
            </label>
          ))}
        </div>
      </fieldset>

      <div className="grid gap-4 md:grid-cols-2">
        <label className="input-group">
          <span>Destination (airport code or city)</span>
          <input
            value={draft.destinationQuery}
            onChange={(event) => updateDraft({ destinationQuery: event.target.value })}
            placeholder="LAX or Los Angeles"
            autoComplete="off"
          />
          <small>Example: `LAX`, `SFO`, `Paris`</small>
        </label>

        <div className="grid grid-cols-2 gap-4">
          <label className="input-group">
            <span>Passengers</span>
            <input
              type="number"
              min={1}
              max={9}
              value={draft.passengersAdults}
              onChange={(event) => updateDraft({ passengersAdults: Number(event.target.value) })}
            />
          </label>

          <label className="input-group">
            <span>Cabin</span>
            <select
              value={draft.cabin}
              onChange={(event) => updateDraft({ cabin: event.target.value as Cabin })}
            >
              <option value="economy">Economy</option>
              <option value="premium_economy">Premium Economy</option>
              <option value="business">Business</option>
              <option value="first">First</option>
            </select>
          </label>
        </div>
      </div>
    </section>
  );
}
