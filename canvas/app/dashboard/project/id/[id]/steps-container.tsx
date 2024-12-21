"use client";
import React from "react";
import { useProjectStore } from "@/stores/project";
import useSWR from "swr";
import { getSteps } from "@/services/step";
import { StepAndJobsSkeleton } from "./view/skeleton/step-and-jobs-skeleton";
import { Steps } from "./steps";
import { getStepSWRKey } from "@/utils/getSWRKey";
import { useSearchParams } from "next/navigation";

export function StepsContainer() {
  const searchParams = useSearchParams();
  const { project, updateSteps, updateCurrentStep } = useProjectStore(
    (state) => ({
      project: state.project,
      updateSteps: state.updateSteps,
      updateCurrentStep: state.updateCurrentStep,
    })
  );

  const { data, error, isLoading } = useSWR(
    getStepSWRKey(project.id),
    () => getSteps({ projectId: project.id, canThrowOnError: true }),
    {
      revalidateIfStale: false,
      revalidateOnFocus: false,
      revalidateOnReconnect: false,
      refreshInterval: 1000 * 60,
    }
  );

  React.useEffect(() => {
    if (data && data.ok && data.response) {
      updateSteps(data.response);
      const stepId = searchParams.get("step") || "";
      const step = data.response.find((step) => step.id === +stepId);

      if (step) {
        updateCurrentStep(step);
      } else {
        updateCurrentStep(data.response[0]);
      }
    }
  }, [data, searchParams, updateSteps, updateCurrentStep]);

  if (isLoading && !data?.ok) {
    return <StepAndJobsSkeleton />;
  }

  if (!data || !data.response || error) {
    return (
      <div className="flex-1 flex flex-col justify-center items-center font-thin text-3xl">
        <p className="text-center">
          Failed to fetch all the steps. Please try again after sometime.
        </p>
      </div>
    );
  }

  return <Steps />;
}
