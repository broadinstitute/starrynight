import { ActionContainer } from "@/app/dashboard/_layout/action-container";
import { TakeCredentials } from "./take-credentials";
import { ProjectRunOrConfigureProject } from "../run-or-configure-project";

export function ProjectActions() {
  return (
    <ActionContainer>
      <TakeCredentials />
      <ProjectRunOrConfigureProject />
    </ActionContainer>
  );
}
