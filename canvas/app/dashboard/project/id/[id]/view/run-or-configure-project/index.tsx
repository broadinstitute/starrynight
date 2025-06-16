import { useProjectStore } from "@/stores/project";
import { ProjectRunProject } from "./run-project";
import { ProjectConfigureProject } from "./configure-project";
import { useMemo } from "react";

export function ProjectRunOrConfigureProject() {
  const { projectStatus } = useProjectStore((store) => ({
    projectStatus: store.projectStatus,
  }));

  const shouldShowConfigureProject = useMemo(() => {
    // Project is not configured.
    if (projectStatus === "configuring" || projectStatus === "not-configured") {
      return true;
    }

    // Project is configured.
    return false;
  }, [projectStatus]);

  // if (shouldShowConfigureProject) {
  return <ProjectConfigureProject />;
  // }

  return <ProjectRunProject />;
}
