"use client";

import { PageSpinner } from "@/components/custom/page-spinner";
import { TProjectStepJob } from "@/services/job";
import { getRun } from "@/services/run";
import React from "react";
import useSWR from "swr";
import { ProjectStepJobRuns } from "./runs";
export type TProjectStepJobRunProps = {
  job: TProjectStepJob;
};

export function ProjectStepJobRunsContainer(props: TProjectStepJobRunProps) {
  const { job } = props;
  const key = `/job/execute?job_id=${job.id}`;
  const { data, error, isLoading } = useSWR(
    key,
    () => getRun({ job_id: job.id, canThrowOnError: true }),
    {
      revalidateIfStale: false,
      revalidateOnFocus: false,
      revalidateOnReconnect: false,
      refreshInterval: 1000 * 30,
    }
  );

  if (isLoading || !data || !data.response) {
    return <PageSpinner />;
  }

  if (error || !data || !data.response) {
    return <div className="text-gray-600">Something went wrong!</div>;
  }

  return <ProjectStepJobRuns job={job} mutateKey={key} runs={data.response} />;
}
