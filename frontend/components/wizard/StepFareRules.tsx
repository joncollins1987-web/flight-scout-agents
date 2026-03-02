import { formatCurrency } from "@/lib/formatters";
import { StepProps } from "./types";

export default function StepFareRules({ draft, updateDraft }: StepProps) {
  return (
    <section className="space-y-6" aria-labelledby="step-fare-rules">
      <div>
        <h3 id="step-fare-rules" className="text-2xl font-semibold text-ink">
          Price & Fare Rules
        </h3>
        <p className="text-sm text-slate-600">Tell the system what cost assumptions should be included in true-total pricing.</p>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <label className="input-group">
          <span>Carry-on count</span>
          <input
            type="number"
            min={0}
            max={5}
            value={draft.carryOnCount}
            onChange={(event) => updateDraft({ carryOnCount: Number(event.target.value) })}
          />
        </label>

        <label className="input-group">
          <span>Checked bag count</span>
          <input
            type="number"
            min={0}
            max={5}
            value={draft.checkedBagCount}
            onChange={(event) => updateDraft({ checkedBagCount: Number(event.target.value) })}
          />
        </label>

        <label className="input-group">
          <span>Target budget (optional)</span>
          <input
            type="number"
            min={0}
            placeholder="450"
            value={draft.targetBudgetUsd}
            onChange={(event) =>
              updateDraft({ targetBudgetUsd: event.target.value === "" ? "" : Number(event.target.value) })
            }
          />
          <small>
            Used for review context. Not a strict filter.
            {draft.targetBudgetUsd !== "" ? ` Current: ${formatCurrency(draft.targetBudgetUsd)}` : ""}
          </small>
        </label>
      </div>

      <fieldset className="surface-card space-y-3 p-4">
        <legend className="text-sm font-semibold text-slate-700">Fare constraints</legend>
        <div className="grid gap-2 md:grid-cols-2">
          <label className="inline-flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={draft.basicEconomyAllowed}
              onChange={(event) => updateDraft({ basicEconomyAllowed: event.target.checked })}
            />
            Basic economy allowed
          </label>
          <label className="inline-flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={draft.refundableRequired}
              onChange={(event) => updateDraft({ refundableRequired: event.target.checked })}
            />
            Refundable fare required
          </label>
        </div>
      </fieldset>
    </section>
  );
}
