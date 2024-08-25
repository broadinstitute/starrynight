"use client";
import React from "react";
import { Sidebar } from "@/components/custom/sidebar";
import { TProjectStep } from "@/services/step";
import { ProjectStepJobs } from "./jobs";
import { Button } from "@/components/ui/button";
import { Loader2, PlayIcon } from "lucide-react";
import { ActionsButtons } from "@/components/custom/action-buttons";
import { useProjectStore } from "@/stores/project";
import useSWR from "swr";
import { ProjectError } from "./project-error";
import { getSteps } from "@/services/step";
import { StepAndJobsSkeleton } from "./skeleton/step-and-jobs-skeleton";
import { Steps } from "./steps";

export function StepsContainer() {
  const { project, updateSteps, updateCurrentStep } = useProjectStore(
    (state) => ({
      project: state.project,
      updateSteps: state.updateSteps,
      updateCurrentStep: state.updateCurrentStep,
    })
  );

  const { data, error, isLoading } = useSWR(
    `/step/?project_id=${project.id}`,
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
      updateCurrentStep(data.response[0]);
    }
  }, [data, updateSteps, updateCurrentStep]);

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
