"use client";

import { useMemo, useState } from "react";

import {
  buildMonthBuckets,
  buildRequestFromDraft,
  buildTripBrief,
  createDefaultDraft,
  DATE_HORIZON_MONTHS,
  flattenMonthDates,
  validateStep,
  WIZARD_STEPS,
} from "@/lib/wizard";
import { SearchWizardProps, WizardStepId } from "@/lib/ui-types";
import StepComfortStops from "./wizard/StepComfortStops";
import StepDateFlex from "./wizard/StepDateFlex";
import StepFareRules from "./wizard/StepFareRules";
import StepRouteTravelers from "./wizard/StepRouteTravelers";
import StepStopoverEngine from "./wizard/StepStopoverEngine";
import TripBriefPanel from "./wizard/TripBriefPanel";

export default function SearchWizard({ loading, onSubmit }: SearchWizardProps) {
  const monthBuckets = useMemo(() => buildMonthBuckets(DATE_HORIZON_MONTHS), []);
  const validDateSet = useMemo(() => new Set(flattenMonthDates(monthBuckets)), [monthBuckets]);
  const [draft, setDraft] = useState(() => createDefaultDraft(monthBuckets));
  const [stepIndex, setStepIndex] = useState(0);

  const currentStep = WIZARD_STEPS[stepIndex];
  const validation = validateStep(currentStep.id, draft, validDateSet);
  const canMoveNext = validation.valid;
  const isLastStep = stepIndex === WIZARD_STEPS.length - 1;

  const progressPercent = Math.round(((stepIndex + 1) / WIZARD_STEPS.length) * 100);

  const updateDraft = (patch: Partial<typeof draft>) => {
    setDraft((prev) => ({ ...prev, ...patch }));
  };

  const handleDefaults = () => {
    setDraft(createDefaultDraft(monthBuckets));
    setStepIndex(0);
  };

  const handleBack = () => {
    setStepIndex((current) => Math.max(0, current - 1));
  };

  const handleNext = () => {
    if (!canMoveNext) {
      return;
    }
    setStepIndex((current) => Math.min(WIZARD_STEPS.length - 1, current + 1));
  };

  const handleSubmit = async () => {
    if (!canMoveNext) {
      return;
    }
    const payload = buildRequestFromDraft(draft);
    await onSubmit(payload);
  };

  const renderStep = (stepId: WizardStepId) => {
    if (stepId === "route_travelers") {
      return <StepRouteTravelers draft={draft} updateDraft={updateDraft} />;
    }
    if (stepId === "date_flex") {
      return <StepDateFlex draft={draft} updateDraft={updateDraft} monthBuckets={monthBuckets} />;
    }
    if (stepId === "price_fare") {
      return <StepFareRules draft={draft} updateDraft={updateDraft} />;
    }
    if (stepId === "comfort_stops") {
      return <StepComfortStops draft={draft} updateDraft={updateDraft} />;
    }
    return <StepStopoverEngine draft={draft} updateDraft={updateDraft} />;
  };

  return (
    <section className="wizard-shell">
      <header className="surface-card p-5">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <p className="eyebrow">Guided Search</p>
            <h2 className="text-2xl font-semibold text-ink">Build your flight brief in five steps</h2>
            <p className="mt-1 text-sm text-slate-600">We keep essential decisions up front and tuck advanced controls where they belong.</p>
          </div>
          <div className="flex gap-2">
            <button type="button" className="button-secondary" onClick={handleDefaults}>
              NYC Weekend Baseline
            </button>
            <button type="button" className="button-ghost" onClick={handleDefaults}>
              Reset
            </button>
          </div>
        </div>

        <div className="mt-5 space-y-3">
          <div className="h-2 rounded-full bg-slate-200">
            <div className="h-full rounded-full bg-gradient-to-r from-sky-500 to-cyan-500 transition-all duration-300" style={{ width: `${progressPercent}%` }} />
          </div>

          <ol className="grid gap-2 md:grid-cols-5" aria-label="Wizard steps">
            {WIZARD_STEPS.map((step, index) => {
              const active = index === stepIndex;
              const complete = index < stepIndex;
              return (
                <li key={step.id} className={`rounded-lg border p-2 text-xs ${active ? "border-sky-300 bg-sky-50" : "border-slate-200 bg-white"}`}>
                  <p className={`font-semibold ${complete ? "text-emerald-700" : "text-slate-700"}`}>{index + 1}. {step.title}</p>
                  <p className="mt-1 text-slate-500">{step.description}</p>
                </li>
              );
            })}
          </ol>
        </div>
      </header>

      <div className="mt-5 grid gap-5 xl:grid-cols-[minmax(0,1fr)_320px]">
        <div className="surface-card p-5 transition-all duration-300 animate-fade-in">
          {renderStep(currentStep.id)}

          {validation.errors.length > 0 ? (
            <div className="alert-card mt-5" role="alert">
              <p className="font-semibold">Before continuing:</p>
              <ul className="mt-1 list-disc space-y-1 pl-5">
                {validation.errors.map((error) => (
                  <li key={error}>{error}</li>
                ))}
              </ul>
            </div>
          ) : null}

          <footer className="mt-6 flex flex-wrap items-center justify-between gap-3 border-t border-slate-200 pt-4">
            <div className="text-xs text-slate-500">Step {stepIndex + 1} of {WIZARD_STEPS.length}</div>
            <div className="flex gap-2">
              <button type="button" className="button-ghost" onClick={handleBack} disabled={stepIndex === 0 || loading}>
                Back
              </button>
              {!isLastStep ? (
                <button type="button" className="button-primary" onClick={handleNext} disabled={!canMoveNext || loading}>
                  Next step
                </button>
              ) : (
                <button type="button" className="button-primary" onClick={handleSubmit} disabled={!canMoveNext || loading}>
                  {loading ? "Running multi-agent search..." : "Run search"}
                </button>
              )}
            </div>
          </footer>
        </div>

        <TripBriefPanel items={buildTripBrief(draft)} />
      </div>
    </section>
  );
}
