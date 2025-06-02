import { ActionContainer } from "@/app/dashboard/_layout/action-container";
import { ProjectRunOrConfigureProject } from "../run-or-configure-project";
import { ProjectDeleteAction } from "./delete-project";
import { ProjectSettings } from "../project-settings";

export function ProjectActions() {
  return (
    <ActionContainer>
      <ProjectSettings />
      <ProjectRunOrConfigureProject />
      <ProjectDeleteAction />
    </ActionContainer>
  );
}
