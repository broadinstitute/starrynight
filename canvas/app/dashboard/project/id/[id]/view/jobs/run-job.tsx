import { ButtonWithTooltip } from "@/components/custom/button-with-tooltip";
import { TJob } from "@/services/job";
import { PlayIcon } from "lucide-react";

export type TProjectJobRunProps = {
  job: TJob;
};

export function ProjectJobRun(props: TProjectJobRunProps) {
  const { job } = props;
  const title = `Run ${job.name}`;

  return (
    <ButtonWithTooltip variant="ghost" size="icon" message={title}>
      <PlayIcon />
    </ButtonWithTooltip>
  );
}
