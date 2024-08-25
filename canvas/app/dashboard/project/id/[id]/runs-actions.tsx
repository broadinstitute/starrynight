import { ActionsButtons } from "@/components/custom/action-buttons";
import { toast } from "@/components/ui/use-toast";
import { executeJob, TProjectStepJob } from "@/services/job";
import { TProjectStepJobRun, TRunStatus } from "@/services/run";
import { useMutation } from "@tanstack/react-query";
import React from "react";
import { mutate } from "swr";

export type TRunsActionsProps = {
  job: TProjectStepJob;
  runs: TProjectStepJobRun[];

  mutateKey: string;
};

export function RunsActions(props: TRunsActionsProps) {
  const { job, runs, mutateKey } = props;

  const [status, setStatus] = React.useState<TRunStatus>("init");

  const {
    mutate: executeJobMutation,
    isPending,
    isSuccess,
    error,
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
    if (isSuccess) {
      // will tell swr to refetch data
      mutate(mutateKey);
      toast({
        title: "Job started successfully",
        className: "bg-black text-white",
      });
    } else if (error) {
      mutate(mutateKey);
      toast({
        title: "Failed to start the Job",
        variant: "destructive",
      });
    }
  }, [error, isSuccess, mutateKey]);

  React.useEffect(() => {
    if (!runs || runs.length === 0) {
      setStatus("init");
    } else {
      setStatus(runs[runs.length - 1].run_status);
    }
  }, [runs]);

  return (
    <ActionsButtons
      currentState={isPending ? "pending" : status}
      cancelButton={{
        isDisabled: isSuccess,
        onClick: () => {
          console.log("Cancel this job");
        },
        tooltipText: "To cancel the job.",
      }}
      playButton={{
        isDisabled: false,
        tooltipText: "To execute this job.",
        onClick: submitJobRequest,
      }}
      pendingButton={{
        isDisabled: false,
        tooltipText: "This job is pending.",
      }}
      runningButton={{
        isDisabled: false,
        tooltipText: "Executing this job.",
      }}
      failedButton={{
        tooltipText:
          "Last execution was failed. Press this button to retry this job.",
        onClick: submitJobRequest,
      }}
    />
  );
}
