import { StopoverEffort } from "@/lib/types";
import { StepProps } from "./types";

export default function StepStopoverEngine({ draft, updateDraft }: StepProps) {
  return (
    <section className="space-y-6" aria-labelledby="step-stopover-engine">
      <div>
        <h3 id="step-stopover-engine" className="text-2xl font-semibold text-ink">
          Stopover + Engine
        </h3>
        <p className="text-sm text-slate-600">Finalize stopover behavior and advanced runtime controls before search.</p>
      </div>

      <fieldset className="surface-card space-y-3 p-4">
        <legend className="text-sm font-semibold text-slate-700">Stopover plan controls</legend>
        <div className="grid gap-2 md:grid-cols-2">
          <label className="inline-flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={draft.stopoverPlanEnabled}
              onChange={(event) => updateDraft({ stopoverPlanEnabled: event.target.checked })}
            />
            Generate stopover plans
          </label>
          <label className="inline-flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={draft.stopoverLeaveAirport}
              onChange={(event) => updateDraft({ stopoverLeaveAirport: event.target.checked })}
            />
            Leave airport when practical
          </label>
          <label className="input-group">
            <span>Stopover budget USD (optional)</span>
            <input
              type="number"
              min={0}
              value={draft.stopoverBudgetUsd}
              onChange={(event) =>
                updateDraft({ stopoverBudgetUsd: event.target.value === "" ? "" : Number(event.target.value) })
              }
            />
          </label>
          <label className="input-group">
            <span>Stopover effort</span>
            <select
              value={draft.stopoverEffort}
              onChange={(event) => updateDraft({ stopoverEffort: event.target.value as StopoverEffort })}
            >
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
            </select>
          </label>
        </div>
      </fieldset>

      <details className="surface-card p-4">
        <summary className="cursor-pointer text-sm font-semibold text-slate-700">Advanced engine controls</summary>
        <p className="mt-2 text-xs text-slate-500">These options affect runtime behavior and diagnostics.</p>

        <div className="mt-3 grid gap-4 md:grid-cols-2">
          <label className="inline-flex items-center gap-2 rounded-lg border border-slate-200 px-3 py-2 text-sm">
            <input
              type="checkbox"
              checked={draft.dryRun}
              onChange={(event) => updateDraft({ dryRun: event.target.checked })}
            />
            Dry run mode (fixtures only)
          </label>

          <label className="input-group">
            <span>Verify top N per tab</span>
            <input
              type="number"
              min={3}
              max={10}
              value={draft.maxVerifyPerTab}
              onChange={(event) => updateDraft({ maxVerifyPerTab: Number(event.target.value) })}
            />
          </label>

          <label className="inline-flex items-center gap-2 rounded-lg border border-slate-200 px-3 py-2 text-sm">
            <input
              type="checkbox"
              checked={draft.sourceFlags.aggregator_one}
              onChange={(event) =>
                updateDraft({ sourceFlags: { ...draft.sourceFlags, aggregator_one: event.target.checked } })
              }
            />
            Enable Aggregator 1
          </label>

          <label className="inline-flex items-center gap-2 rounded-lg border border-slate-200 px-3 py-2 text-sm">
            <input
              type="checkbox"
              checked={draft.sourceFlags.aggregator_two}
              onChange={(event) =>
                updateDraft({ sourceFlags: { ...draft.sourceFlags, aggregator_two: event.target.checked } })
              }
            />
            Enable Aggregator 2
          </label>
        </div>
      </details>
    </section>
  );
}
