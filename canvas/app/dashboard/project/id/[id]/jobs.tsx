"use client";

import { getJobs } from "@/services/job";
import { TProjectStep } from "@/services/step";
import useSWR from "swr";
import { Accordion } from "@/components/ui/accordion";
import { ProjectStepJob } from "./job";
import { JobsSkeleton } from "./skeleton/jobs-skeleton";
import { Button } from "@/components/ui/button";

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

  if (isLoading && !data) {
    return <JobsSkeleton />;
  }

  if (error || !data || !data.response) {
    return <div>Failed to load jobs. Try again after sometime.</div>;
  }

  return (
    <div className="flex flex-col flex-1 overflow-auto">
      <h4 className="font-bold text-2xl">{step.name}</h4>
      <div className="py-4">
        <p>
          This step includes {data.response.length} job(s). You can run each job
          individually or use the &quot;Execute Step&quot; button to run all
          jobs at once.
        </p>
        <br />
        <Button size="sm">Execute Step</Button>
      </div>
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
