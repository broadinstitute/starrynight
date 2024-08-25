import { ActionsButtons } from "@/components/custom/action-buttons";
import { toast } from "@/components/ui/use-toast";
import { executeJob, TProjectStepJob } from "@/services/job";
import { TRunStatus } from "@/services/run";
import { useMutation } from "@tanstack/react-query";
import React from "react";
import { mutate } from "swr";

export type TRunsActionsProps = {
  job: TProjectStepJob;
  mutateKey: string;
};

export function RunsActions(props: TRunsActionsProps) {
  const { job, mutateKey } = props;

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
        title: "Job completed successfully",
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
  const [currentState, setCurrentState] = React.useState<TRunStatus>("init");

  React.useEffect(() => {
    if (isSuccess) {
      setCurrentState("running");
    } else if (error) {
      setCurrentState("failed");
    } else if (isPending) {
      setCurrentState("pending");
    }
  }, [error, isPending, isSuccess]);

  return (
    <ActionsButtons
      currentState={currentState}
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
      successButton={{
        isDisabled: false,
        onClick: () => {
          setCurrentState("pending");
        },
        tooltipText: "Click to run this job again.",
      }}
      failedButton={{
        tooltipText:
          "Last execution was failed. Press this button to retry this job.",
        onClick: () => {
          setCurrentState("pending");
          setTimeout(() => {
            setCurrentState("running");
          }, 3000);

          setTimeout(() => {
            setCurrentState("success");
          }, 6000);
        },
      }}
    />
  );
}
