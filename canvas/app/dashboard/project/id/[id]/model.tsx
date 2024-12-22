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
  const { data, error, isLoading } = useGetProject({
    id: projectId,
  });

  if (isLoading) {
    return <ProjectSkeleton />;
  }

  if (error || !data) {
    return <ProjectError />;
  }

  return <ProjectView project={data} />;
}
