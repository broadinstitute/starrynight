"use client";

import { PageSpinner } from "@/components/custom/page-spinner";
import { Button } from "@/components/ui/button";
import { toast } from "@/components/ui/use-toast";
import { TProjectStepJob } from "@/services/job";
import { createRun, getRun } from "@/services/run";
import { useMutation } from "@tanstack/react-query";
import { Loader2 } from "lucide-react";
import React from "react";
import useSWR, { mutate } from "swr";

export type TProjectStepJobRunProps = {
  job: TProjectStepJob;
};

export function ProjectStepJobRun(props: TProjectStepJobRunProps) {
  const { job } = props;
  const key = `/run?job_id=${job.id}`;
  const { data, error, isLoading } = useSWR(
    key,
    () => getRun({ job_id: job.id, canThrowOnError: true }),
    {
      revalidateIfStale: false,
      revalidateOnFocus: false,
      revalidateOnReconnect: false,
      refreshInterval: 1000 * 60 * 2,
    }
  );

  const {
    mutate: createNewRun,
    isPending: isSubmittingJob,
    isSuccess: isSubmittedSuccessfully,
    error: isFailedToExecute,
  } = useMutation({
    mutationFn: createRun,
  });

  function executeJob() {
    createNewRun({
      id: 0,
      jobId: job.id,
      name: job.name,
      canThrowOnError: true,
    });
  }

  React.useEffect(() => {
    if (isSubmittedSuccessfully) {
      // will tell swr to refetch data
      mutate(key);
      toast({
        title: "Job started successfully",
      });
    } else if (isFailedToExecute) {
      toast({
        title: "Failed to start the Job",
      });
    }
  }, [isFailedToExecute, isSubmittedSuccessfully, key]);

  if (isLoading || !data || !data.response) {
    return <PageSpinner />;
  }

  if (error || !data || !data.response) {
    return <div className="text-gray-600">Something went wrong!</div>;
  }

  if (data.response.length === 0) {
    return (
      <div>
        <p className="mb-4">No job is running.</p>
        <Button disabled={isSubmittingJob} size="sm" onClick={executeJob}>
          {isSubmittingJob && <Loader2 className="h-3 w-3 animate-spin mr-1" />}
          Execute a new job
        </Button>
      </div>
    );
  }
  return <div>Job is running.</div>;
}
