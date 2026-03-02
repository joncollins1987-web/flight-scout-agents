import { StopoverPlan } from "@/lib/types";
import { formatCurrency, formatMinutes } from "@/lib/formatters";

interface Props {
  plan: StopoverPlan;
}

export default function StopoverPanel({ plan }: Props) {
  return (
    <div className="emphasis-card space-y-3 p-4 text-sm">
      <header className="flex flex-wrap items-center justify-between gap-2">
        <p className="font-semibold text-ink">Stopover playbook • {plan.layover_airport}</p>
        {typeof plan.budget_fit === "boolean" ? (
          <span className={plan.budget_fit ? "chip-verified" : "chip-warning"}>
            {plan.budget_fit ? "Within budget" : "Over budget"}
          </span>
        ) : (
          <span className="chip-muted">No budget cap</span>
        )}
      </header>

      <div className="grid gap-2 md:grid-cols-3">
        <div className="timeline-card">
          <p className="timeline-title">Usable time</p>
          <p className="timeline-main">{formatMinutes(plan.usable_time_minutes)}</p>
        </div>
        <div className="timeline-card">
          <p className="timeline-title">Transit estimate</p>
          <p className="timeline-main">{formatMinutes(plan.transit_time_minutes_est)}</p>
        </div>
        <div className="timeline-card">
          <p className="timeline-title">Transit cost</p>
          <p className="timeline-main">{formatCurrency(plan.transit_cost_usd_est)}</p>
        </div>
      </div>

      <ul className="list-disc space-y-1 pl-5 text-slate-700">
        {plan.bullets.map((bullet) => (
          <li key={bullet}>{bullet}</li>
        ))}
      </ul>

      {plan.warnings.length > 0 ? (
        <ul className="list-disc space-y-1 pl-5 text-amber-700">
          {plan.warnings.map((warning) => (
            <li key={warning}>{warning}</li>
          ))}
        </ul>
      ) : null}
    </div>
  );
}
