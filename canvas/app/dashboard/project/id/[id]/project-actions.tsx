import { ActionsButtons } from "@/components/custom/action-buttons";
import { TRunStatus } from "@/services/run";
import React from "react";

export function ProjectActions() {
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
        tooltipText: "To cancel all the steps running in this Project.",
      }}
      playButton={{
        isDisabled: false,
        tooltipText: "To run all the steps in the current project.",
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
        tooltipText: "Project execution is in pending.",
      }}
      runningButton={{
        isDisabled: false,
        tooltipText: "Executing all the steps in the current project.",
      }}
      successButton={{
        isDisabled: false,
        onClick: () => {
          setCurrentState("pending");
        },
        tooltipText: "Click to run all the steps in the project again.",
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
