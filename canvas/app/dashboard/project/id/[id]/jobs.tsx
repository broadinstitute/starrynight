"use client";

import { getJobs } from "@/services/job";
import { TProjectStep } from "@/services/step";
import useSWR from "swr";
import { Accordion } from "@/components/ui/accordion";
import { ProjectStepJob } from "./job";
import { JobsSkeleton } from "./view/skeleton/jobs-skeleton";
import { JobsActions } from "./jobs-actions";
import React from "react";
import { useProjectStore } from "@/stores/project";

export function ProjectStepJobs() {
  const { step, updateJobs } = useProjectStore((state) => ({
    step: state.currentStep,
    updateJobs: state.updateCurrentStepJobs,
  }));

  const { data, error, isLoading } = useSWR(
    `/job/?step_id=${step!.id}`,
    () => getJobs({ stepId: step!.id, canThrowOnError: true }),
    {
      revalidateIfStale: false,
      revalidateOnFocus: false,
      revalidateOnReconnect: false,
      refreshInterval: 1000 * 60 * 2,
    }
  );

  React.useEffect(() => {
    if (data && data.response) {
      updateJobs(data.response);
    }
  }, [updateJobs, data]);

  if (isLoading && !data) {
    return <JobsSkeleton />;
  }

  if (error || !data || !data.response) {
    return <div>Failed to load jobs. Try again after sometime.</div>;
  }

  return (
    <div className="flex flex-col flex-1 overflow-auto">
      <h4 className="font-bold text-2xl">{step!.name}</h4>
      <div className="py-4 flex justify-between">
        <p className="pt-2">{step!.description}</p>
        <div>
          <JobsActions />
        </div>
      </div>
      <div className="mt-4">
        <Accordion
          type="multiple"
          defaultValue={data.response.map((res) => `job-${res.id}-${step!.id}`)}
        >
          {data.response.map((job) => (
            <ProjectStepJob key={`${job.id} ${step!.id}`} job={job} />
          ))}
        </Accordion>
      </div>
    </div>
  );
}
