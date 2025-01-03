import { ActionButton } from "@/components/custom/action-button";
import { FeatureNotImplementedModal } from "@/components/custom/feature-not-implemented-modal";
import { PlayIcon } from "lucide-react";
import { useCallback } from "react";

export type TProjectSidebarRunStepProps = {
  stepId: string | number;
};

export function ProjectSidebarRunStep(props: TProjectSidebarRunStepProps) {
  const { stepId } = props;

  const handleOnClick = useCallback((event: React.MouseEvent) => {
    // TODO: add the feature to run the step.
  }, []);

  return (
    <FeatureNotImplementedModal featureName="Run Step">
      <ActionButton
        onClick={handleOnClick}
        className="hover:bg-slate-200"
        message="Run"
        icon={<PlayIcon />}
      />
    </FeatureNotImplementedModal>
  );
}
