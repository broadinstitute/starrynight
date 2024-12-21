"use client";

import { useGetProject } from "@/services/projects";
import { ProjectSkeleton } from "./view/skeleton";
import { ProjectError } from "./project-error";
import { ProjectView } from "./view";

export type TProjectModelProps = {
  projectId: string;
};

export function ProjectModel(props: TProjectModelProps) {
  const { projectId } = props;
  const {
    data: project,
    error: projectError,
    isLoading: isProjectLoading,
  } = useGetProject({
    id: projectId,
  });

  if (isProjectLoading) {
    return <ProjectSkeleton />;
  }

  if (projectError || !project || !project.response) {
    return <ProjectError />;
  }

  return <ProjectView project={project.response} />;
}
