"use client";

import { PageSpinner } from "@/components/custom/page-spinner";
import { Button } from "@/components/ui/button";
import { toast } from "@/components/ui/use-toast";
import { executeJob, TProjectStepJob } from "@/services/job";
import { getRun } from "@/services/run";
import { useMutation } from "@tanstack/react-query";
import { Loader2 } from "lucide-react";
import React from "react";
import useSWR, { mutate } from "swr";
import { JobBadge } from "./badge";
import { FileViewer } from "@/components/custom/file-viewer";

export type TProjectStepJobRunProps = {
  job: TProjectStepJob;
};

export function ProjectStepJobRun(props: TProjectStepJobRunProps) {
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

  const {
    mutate: executeJobMutation,
    isPending: isSubmittingJob,
    isSuccess: isSubmittedSuccessfully,
    error: isFailedToExecute,
  } = useMutation({
    mutationFn: executeJob,
  });

  function submitJobRequest() {
    executeJobMutation({
      jobId: job.id,
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
        <Button disabled={isSubmittingJob} size="sm" onClick={submitJobRequest}>
          {isSubmittingJob && <Loader2 className="h-3 w-3 animate-spin mr-1" />}
          Execute new run
        </Button>
      </div>
    );
  }
  return (
    <div>
      <div className="font-bold mb-4">Jobs:</div>

      {data.response.map((run, idx) => (
        <div key={run.id}>
          <div className="space-y-2">
            <div>Name: {run.name}</div>
            <div>
              Status: <JobBadge status={run.run_status} />
            </div>
            {run.run_status === "success" && (
              <div>
                <FileViewer fileName="s3_file_url.test" />
              </div>
            )}
          </div>
          {idx !== data.response!.length - 1 && <hr className="my-4" />}
        </div>
      ))}

      <Button
        disabled={isSubmittingJob}
        size="sm"
        className="mt-4"
        onClick={submitJobRequest}
      >
        {isSubmittingJob && <Loader2 className="h-3 w-3 animate-spin mr-1" />}
        Execute new run
      </Button>
    </div>
  );
}
