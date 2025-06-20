"use client";

import { TProject } from "@/services/projects";
import { ProjectStoreProvider, useProjectStore } from "@/stores/project";
import { ProjectHeading } from "./heading";
import { ProjectMainContainer } from "./main-container";
import { ProjectJobs } from "./jobs";

export type TProjectViewProps = {
  project: TProject;
};

export function ProjectView(props: TProjectViewProps) {
  const { project } = props;

  return (
    <ProjectStoreProvider project={project}>
      <ProjectHeading />
      <ProjectDescription />
      <ProjectMainContainer>
        <ProjectJobs />
      </ProjectMainContainer>
    </ProjectStoreProvider>
  );
}

function ProjectDescription() {
  const { projectStatus, description } = useProjectStore((store) => ({
    projectStatus: store.projectStatus,
    description: store.project.description,
  }));

  if (projectStatus === "configuring" || projectStatus === "not-configured") {
    // TODO: Add description.
    return <div className="px-4 py-2 text-gray-600">{description}</div>;
  }

  return null;
}
