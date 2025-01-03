import { ButtonWithTooltip } from "@/components/custom/button-with-tooltip";
import { TJob } from "@/services/job";
import { PlayIcon } from "lucide-react";
import React from "react";
import { useRunJob } from "./use-run-job";
import { ActionButton } from "@/components/custom/action-button";

export type TProjectJobRunProps = {
  job: TJob;
};

export function ProjectJobRun(props: TProjectJobRunProps) {
  const { job } = props;
  const title = `Run ${job.name}`;

  const { run, isLoading } = useRunJob({ job });

  return (
    <ActionButton
      onClick={run as () => void}
      message={title}
      isLoading={isLoading}
      icon={<PlayIcon />}
    />
  );
}
