import { ActionContainer } from "@/app/dashboard/_layout/action-container";
import { Button } from "@/components/ui/button";
import { PlayIcon } from "lucide-react";
import { TakeCredentials } from "./take-credentials";
import { FeatureNotImplementedModal } from "@/components/custom/feature-not-implemented-modal";

export function ProjectActions() {
  return (
    <ActionContainer>
      <TakeCredentials />
      <FeatureNotImplementedModal featureName="Run project">
        <Button className="md:w-40">
          <PlayIcon /> Run project
        </Button>
      </FeatureNotImplementedModal>
    </ActionContainer>
  );
}
