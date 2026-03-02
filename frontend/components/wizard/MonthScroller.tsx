"use client";

import { useMemo, useState } from "react";

import { formatDayChip } from "@/lib/formatters";
import { MonthBucket } from "@/lib/ui-types";

interface Props {
  legend: string;
  description: string;
  prefix: "depart" | "return";
  monthBuckets: MonthBucket[];
  selectedDates: string[];
  onToggleDate: (value: string) => void;
}

export default function MonthScroller({
  legend,
  description,
  prefix,
  monthBuckets,
  selectedDates,
  onToggleDate,
}: Props) {
  const firstMonthKey = monthBuckets[0]?.monthKey ?? "";
  const selectedMonthKey = useMemo(() => {
    const firstSelected = selectedDates[0];
    if (!firstSelected) return firstMonthKey;
    const key = firstSelected.slice(0, 7);
    return monthBuckets.some((month) => month.monthKey === key) ? key : firstMonthKey;
  }, [firstMonthKey, monthBuckets, selectedDates]);

  const [activeMonthKey, setActiveMonthKey] = useState<string>(selectedMonthKey);

  const activeMonth =
    monthBuckets.find((month) => month.monthKey === activeMonthKey) ?? monthBuckets[0];

  return (
    <fieldset className="surface-card space-y-3 p-4">
      <legend className="text-sm font-semibold text-slate-700">{legend}</legend>
      <p className="text-xs text-slate-500">{description}</p>

      <div className="month-toolbar">
        <label className="input-group month-select-group">
          <span>Month</span>
          <select
            value={activeMonth?.monthKey ?? ""}
            onChange={(event) => setActiveMonthKey(event.target.value)}
            aria-label={`${legend} month`}
          >
            {monthBuckets.map((month) => (
              <option key={`${prefix}-${month.monthKey}`} value={month.monthKey}>
                {month.monthLabel}
              </option>
            ))}
          </select>
        </label>
        <p className="text-xs text-slate-500">{selectedDates.length} selected total</p>
      </div>

      {activeMonth ? (
        <div className="month-card" aria-label={activeMonth.monthLabel}>
          <p className="month-label">{activeMonth.monthLabel}</p>
          <div className="month-days">
            {activeMonth.dates.map((date) => {
              const checked = selectedDates.includes(date);
              return (
                <label
                  key={`${prefix}-${date}`}
                  className={`day-chip ${checked ? "day-chip-selected" : "day-chip-unselected"}`}
                >
                  <input
                    type="checkbox"
                    checked={checked}
                    onChange={() => onToggleDate(date)}
                    aria-label={`${legend} ${date}`}
                  />
                  <span>{formatDayChip(date)}</span>
                </label>
              );
            })}
          </div>
        </div>
      ) : (
        <p className="text-sm text-slate-500">No months available.</p>
      )}
    </fieldset>
  );
}
