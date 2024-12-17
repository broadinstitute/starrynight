import { ActionContainer } from "@/components/custom/action-container";
import { Button } from "@/components/ui/button";
import { PlayIcon, XIcon } from "lucide-react";
import { TakeCredentials } from "./take-credentials";

export function ProjectActions() {
  return (
    <ActionContainer>
      <TakeCredentials />
      <Button>
        <PlayIcon /> Run project
      </Button>
    </ActionContainer>
  );
}
