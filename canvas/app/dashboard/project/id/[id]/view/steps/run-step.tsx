import { ButtonWithTooltip } from "@/components/custom/button-with-tooltip";
import { PlayIcon } from "lucide-react";
import { useCallback } from "react";

export type TProjectSidebarRunStepProps = {
  stepId: string | number;
};

export function ProjectSidebarRunStep(props: TProjectSidebarRunStepProps) {
  const { stepId } = props;

  const handleOnClick = useCallback(
    (event: React.MouseEvent) => {
      event.preventDefault();
      event.stopPropagation();

      console.log("Running step id:", stepId);
    },
    [stepId]
  );

  return (
    <ButtonWithTooltip
      onClick={handleOnClick}
      variant="ghost"
      size="icon"
      className="hover:bg-slate-200"
      message="Run"
    >
      <PlayIcon />
    </ButtonWithTooltip>
  );
}
