import { MonthBucket, SearchDraft } from "@/lib/ui-types";

export interface StepProps {
  draft: SearchDraft;
  updateDraft: (patch: Partial<SearchDraft>) => void;
}

export interface DateStepProps extends StepProps {
  monthBuckets: MonthBucket[];
}
