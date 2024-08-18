"use client";

import { PageSpinner } from "@/components/custom/page-spinner";
import { getJobs } from "@/services/job";
import { TProjectStep } from "@/services/step";
import useSWR from "swr";
import { ProjectError } from "./project-error";
import { Accordion } from "@/components/ui/accordion";
import { ProjectStepJob } from "./job";

export type TProjectStepJobProps = {
  step: TProjectStep;
};

export function ProjectStepJobs(props: TProjectStepJobProps) {
  const { step } = props;
  const { data, error, isLoading } = useSWR(
    `/job/?step_id=${step.id}`,
    () => getJobs({ stepId: step.id, canThrowOnError: true }),
    {
      revalidateIfStale: false,
      revalidateOnFocus: false,
      revalidateOnReconnect: false,
      refreshInterval: 1000 * 60 * 2,
    }
  );

  if (isLoading || !data || !data.response) {
    return <PageSpinner />;
  }

  if (error || !data || !data.response) {
    return <ProjectError />;
  }

  return (
    <div className="flex flex-col flex-1 overflow-auto">
      <h4 className="font-bold text-2xl">{step.name}</h4>

      <div className="mt-4">
        <Accordion type="single" collapsible>
          {data.response.map((job) => (
            <ProjectStepJob key={job.id} job={job} />
          ))}
        </Accordion>
      </div>
    </div>
  );
}
