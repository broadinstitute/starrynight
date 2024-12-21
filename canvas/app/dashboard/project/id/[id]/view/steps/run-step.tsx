import { ActionButton } from "@/components/custom/action-button";
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
    <ActionButton
      onClick={handleOnClick}
      className="hover:bg-slate-200"
      message="Run"
      icon={<PlayIcon />}
    />
  );
}
