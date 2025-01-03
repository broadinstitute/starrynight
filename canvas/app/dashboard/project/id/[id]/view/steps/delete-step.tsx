import { ActionButton } from "@/components/custom/action-button";
import { FeatureNotImplementedModal } from "@/components/custom/feature-not-implemented-modal";
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

  const handleOnClick = React.useCallback((event: React.MouseEvent) => {
    // TODO: add the feature to delete the step.
  }, []);

  return (
    <FeatureNotImplementedModal featureName="Delete Step">
      <ActionButton
        onClick={handleOnClick}
        className="text-red-500 hover:bg-red-50 hover:text-red-500"
        message="Delete"
        icon={<Trash2 />}
      />
    </FeatureNotImplementedModal>
  );
}
