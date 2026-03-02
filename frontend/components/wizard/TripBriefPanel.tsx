import { SearchSummaryItem } from "@/lib/ui-types";

interface Props {
  items: SearchSummaryItem[];
}

const ORDER: SearchSummaryItem["section"][] = ["Trip", "Dates", "Fare", "Comfort", "Engine"];

function toneClass(tone: SearchSummaryItem["tone"]): string {
  if (tone === "good") return "text-emerald-700";
  if (tone === "warning") return "text-amber-700";
  return "text-slate-700";
}

export default function TripBriefPanel({ items }: Props) {
  return (
    <aside className="surface-card sticky top-4 p-4" aria-label="Trip brief summary">
      <h3 className="text-lg font-semibold text-ink">Trip Brief</h3>
      <p className="mt-1 text-xs text-slate-500">Live summary of your current search setup.</p>

      <div className="mt-4 space-y-4">
        {ORDER.map((section) => {
          const sectionItems = items.filter((item) => item.section === section);
          if (!sectionItems.length) return null;
          return (
            <section key={section} className="space-y-2 border-t border-slate-200 pt-3 first:border-t-0 first:pt-0">
              <h4 className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">{section}</h4>
              <dl className="space-y-1">
                {sectionItems.map((item) => (
                  <div key={item.id} className="text-sm">
                    <dt className="text-xs text-slate-500">{item.label}</dt>
                    <dd className={toneClass(item.tone)}>{item.value}</dd>
                  </div>
                ))}
              </dl>
            </section>
          );
        })}
      </div>
    </aside>
  );
}
