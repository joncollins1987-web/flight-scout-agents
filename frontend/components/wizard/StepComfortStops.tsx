import { StepProps } from "./types";

export default function StepComfortStops({ draft, updateDraft }: StepProps) {
  return (
    <section className="space-y-6" aria-labelledby="step-comfort-stops">
      <div>
        <h3 id="step-comfort-stops" className="text-2xl font-semibold text-ink">
          Comfort & Stops
        </h3>
        <p className="text-sm text-slate-600">Control travel rhythm, connection risk, and preferred carriers.</p>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <label className="input-group">
          <span>Earliest depart (optional)</span>
          <input
            type="time"
            value={draft.earliestDepartLocal}
            onChange={(event) => updateDraft({ earliestDepartLocal: event.target.value })}
          />
        </label>
        <label className="input-group">
          <span>Latest arrive (optional)</span>
          <input
            type="time"
            value={draft.latestArriveLocal}
            onChange={(event) => updateDraft({ latestArriveLocal: event.target.value })}
          />
        </label>
      </div>

      <fieldset className="surface-card space-y-3 p-4">
        <legend className="text-sm font-semibold text-slate-700">Stops and layovers</legend>
        <div className="grid gap-2 md:grid-cols-2">
          <label className="inline-flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={draft.allowStopovers}
              onChange={(event) => updateDraft({ allowStopovers: event.target.checked })}
            />
            Allow stopovers
          </label>
          <label className="inline-flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={draft.preferNonstop}
              onChange={(event) => updateDraft({ preferNonstop: event.target.checked })}
            />
            Prefer nonstop
          </label>
          <label className="input-group md:col-span-2">
            <span>Max layover minutes (optional)</span>
            <input
              type="number"
              min={30}
              value={draft.maxLayoverMinutes}
              onChange={(event) =>
                updateDraft({ maxLayoverMinutes: event.target.value === "" ? "" : Number(event.target.value) })
              }
            />
          </label>
        </div>
      </fieldset>

      <fieldset className="surface-card space-y-3 p-4">
        <legend className="text-sm font-semibold text-slate-700">Comfort preferences</legend>
        <div className="grid gap-2 md:grid-cols-2">
          <label className="inline-flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={draft.avoidRedEyes}
              onChange={(event) => updateDraft({ avoidRedEyes: event.target.checked })}
            />
            Avoid red-eyes
          </label>
          <label className="inline-flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={draft.avoidTightConnections}
              onChange={(event) => updateDraft({ avoidTightConnections: event.target.checked })}
            />
            Avoid tight connections
          </label>
        </div>
      </fieldset>

      <details className="surface-card p-4">
        <summary className="cursor-pointer text-sm font-semibold text-slate-700">Advanced airline constraints</summary>
        <p className="mt-2 text-xs text-slate-500">Optional. Use comma-separated IATA airline codes, e.g. DL,AA.</p>
        <div className="mt-3 grid gap-4 md:grid-cols-2">
          <label className="input-group">
            <span>Preferred airlines</span>
            <input
              value={draft.preferredAirlines}
              onChange={(event) => updateDraft({ preferredAirlines: event.target.value })}
              placeholder="DL,AA"
            />
          </label>
          <label className="input-group">
            <span>Blocked airlines</span>
            <input
              value={draft.blockedAirlines}
              onChange={(event) => updateDraft({ blockedAirlines: event.target.value })}
              placeholder="F9,NK"
            />
          </label>
        </div>
      </details>
    </section>
  );
}
