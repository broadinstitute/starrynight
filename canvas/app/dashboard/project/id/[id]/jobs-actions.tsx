import { ActionsButtons } from "@/components/custom/action-buttons";
import { TRunStatus } from "@/services/run";
import React from "react";

export function JobsActions() {
  const [currentState, setCurrentState] = React.useState<TRunStatus>("init");

  return (
    <ActionsButtons
      currentState={currentState}
      cancelButton={{
        isDisabled:
          currentState === "init" ||
          currentState === "failed" ||
          currentState === "success",
        onClick: () => {
          setCurrentState("failed");
        },
        tooltipText: "To cancel all the jobs running.",
      }}
      playButton={{
        isDisabled: false,
        tooltipText: "To run all the jobs in the current step.",
        onClick: () => {
          setCurrentState("pending");
          setTimeout(() => {
            setCurrentState("running");
          }, 3000);
          setTimeout(() => {
            setCurrentState("failed");
          }, 5000);
        },
      }}
      pendingButton={{
        isDisabled: false,
        tooltipText: "All jobs execution is in pending.",
      }}
      runningButton={{
        isDisabled: false,
        tooltipText: "Executing all the jobs in the current steps.",
      }}
      successButton={{
        isDisabled: false,
        onClick: () => {
          setCurrentState("pending");
        },
        tooltipText: "Click to run all the jobs again.",
      }}
      failedButton={{
        tooltipText:
          "Last execution was failed. Press this button to retry the execution.",
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
