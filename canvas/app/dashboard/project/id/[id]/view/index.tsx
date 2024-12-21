"use client";

import { TProject } from "@/services/projects";
import { ProjectStoreProvider } from "@/stores/project";
import { ProjectHeading } from "./heading";
import { ProjectMainContainer } from "./main-container";
import { ProjectSteps } from "./steps";
import { ProjectJobs } from "./jobs";
import { TStep } from "@/services/step";

export type TProjectViewProps = {
  project: TProject;
};

export function ProjectView(props: TProjectViewProps) {
  const { project } = props;
  return (
    <ProjectStoreProvider project={project}>
      <ProjectHeading />
      <ProjectMainContainer>
        <ProjectSteps />
        <ProjectJobs />
      </ProjectMainContainer>
    </ProjectStoreProvider>
  );
}
