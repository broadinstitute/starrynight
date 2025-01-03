import { FeatureNotImplementedModal } from "@/components/custom/feature-not-implemented-modal";
import { Button } from "@/components/ui/button";
import { PlusIcon } from "lucide-react";
import React from "react";

export function ProjectSidebarAddStep() {
  const handleOnClick = React.useCallback((event: React.MouseEvent) => {
    // TODO: Add a logic to add a new step
  }, []);

  return (
    <FeatureNotImplementedModal featureName="Add A New Step">
      <Button
        onClick={handleOnClick}
        variant="ghost"
        size="icon"
        className="hover:bg-slate-200"
      >
        <PlusIcon />
      </Button>
    </FeatureNotImplementedModal>
  );
}
