import { ToastAction } from "@/components/ui/toast";
import { useToast } from "@/components/ui/use-toast";
import { PROJECT_URL } from "@/constants/routes";
import { TJob, TJobExecuteResponse, useExecuteJob } from "@/services/job";
import { GET_RUNS_QUERY_KEY } from "@/services/run";
import { useProjectStore } from "@/stores/project";
import { useQueryClient } from "@tanstack/react-query";
import Link from "next/link";
import React from "react";

export type TUseRunJobOptions = {
  job: TJob;
};

export function useRunJob(options: TUseRunJobOptions) {
  const { job } = options;
  const { toast, dismiss } = useToast();

  const { project } = useProjectStore((state) => ({
    project: state.project,
  }));

  const queryClient = useQueryClient();

  const jobDescription = React.useMemo(() => {
    return `Job "${job.name}" of project "${project.name}"`;
  }, [job.name, project.name]);

  const jobURL = React.useMemo(() => {
    return `${PROJECT_URL}/${project.id}`;
  }, [project.id]);

  const _handleOnError = React.useCallback(() => {
    const { id } = toast({
      title: "Error: Job failed to run",
      description: ` ${jobDescription} failed to execute.`,
      variant: "destructive",
      action: (
        <ToastAction altText="View Job" onClick={() => dismiss(id)}>
          <Link href={jobURL}>View Job</Link>
        </ToastAction>
      ),
    });
  }, [dismiss, jobDescription, jobURL, toast]);

  const _handleOnSuccess = React.useCallback(
    (data: TJobExecuteResponse) => {
      queryClient.invalidateQueries({
        queryKey: [GET_RUNS_QUERY_KEY, data.job_id],
      });

      const { id } = toast({
        title: "Job started successfully",
        description: `${jobDescription} has been started successfully.`,
        variant: "default",
        action: (
          <ToastAction altText="View Job" onClick={() => dismiss(id)}>
            <Link href={jobURL}>View Job</Link>
          </ToastAction>
        ),
      });
    },
    [toast, jobDescription, jobURL, dismiss, queryClient]
  );

  const { mutate: run, isPending } = useExecuteJob({
    jobId: job.id,
    onError: _handleOnError,
    onSuccess: _handleOnSuccess,
  });

  return {
    run,
    isLoading: isPending,
  };
}
