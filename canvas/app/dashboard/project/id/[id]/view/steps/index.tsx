import { useGetSteps } from "@/services/step";
import { useProjectStore } from "@/stores/project";
import React from "react";
import { StepSidebar } from "./sidebar";
import { SidebarSkeleton } from "../skeleton/sidebar";

export function ProjectSteps() {
  const { projectId } = useProjectStore((state) => ({
    projectId: state.project.id,
  }));

  const { data, error, isLoading } = useGetSteps({ id: projectId });

  if (isLoading) {
    return <SidebarSkeleton />;
  }

  if (!data || error) {
    return (
      <div className="text-red-500 md:pt-4 md:col-span-3">
        Failed to load steps. Please Refresh the page or try again later.
      </div>
    );
  }

  return <StepSidebar steps={data} />;
}
