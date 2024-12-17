import { ButtonWithTooltip } from "@/components/custom/button-with-tooltip";
import { TJob } from "@/services/job";
import { FileInput } from "lucide-react";
import { JobInputModal } from "../modal/job-inputs";

export type TProjectJobInputProps = {
  job: TJob;
};

export function ProjectJobInput(props: TProjectJobInputProps) {
  const { job } = props;
  const title = `${job.name} inputs`;

  return (
    <JobInputModal
      title={title}
      trigger={
        <ButtonWithTooltip variant="ghost" size="icon" message={title}>
          <FileInput />
        </ButtonWithTooltip>
      }
    />
  );
}
