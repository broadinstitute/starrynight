import { ButtonWithTooltip } from "@/components/custom/button-with-tooltip";
import { Trash2 } from "lucide-react";
import React from "react";

export type TProjectSidebarDeleteStepProps = {
  stepId: string | number;
  stepName: string;
};

export function ProjectSidebarDeleteStep(
  props: TProjectSidebarDeleteStepProps
) {
  const { stepId } = props;

  const handleOnClick = React.useCallback(
    (event: React.MouseEvent) => {
      event.preventDefault();
      event.stopPropagation();

      console.log("Deleting step id:", stepId);
    },
    [stepId]
  );

  return (
    <ButtonWithTooltip
      onClick={handleOnClick}
      variant="ghost"
      size="icon"
      className="text-red-500 hover:bg-red-50 hover:text-red-500"
      message="Delete"
    >
      <Trash2 />
    </ButtonWithTooltip>
  );
}
