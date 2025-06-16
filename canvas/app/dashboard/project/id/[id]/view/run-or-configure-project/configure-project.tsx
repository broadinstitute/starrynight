import React from "react";

import { ActionButton } from "@/components/custom/action-button";
import { useToast } from "@/components/ui/use-toast";
import { useConfigureProject } from "@/services/projects";
import { useProjectStore } from "@/stores/project";
import { PlayIcon } from "lucide-react";

export function ProjectConfigureProject() {
  const { projectID, jobStatus, updateProjectStatus } = useProjectStore(
    (store) => ({
      projectID: store.project.id,
      jobStatus: store.jobStatus,
      updateProjectStatus: store.updateProjectStatus,
    }),
  );

  const { toast } = useToast();

  const handleOnConfigureProjectSuccess = React.useCallback(async () => {
    updateProjectStatus("configured");
    toast({
      title: "Project configured successfully!",
      variant: "default",
    });
  }, [updateProjectStatus, toast]);

  const handleOnConfigureProjectError = React.useCallback(() => {
    toast({
      title: "Error configuring the project!",
      variant: "destructive",
    });

    updateProjectStatus("not-configured");
  }, [toast, updateProjectStatus]);

  const { mutate: configureProject, isPending: isConfiguringProject } =
    useConfigureProject({
      onSuccess: handleOnConfigureProjectSuccess,
      onError: handleOnConfigureProjectError,
    });

  const [canConfigureProject, setCanConfigureProject] = React.useState(false);

  const handleOnConfigureProject = React.useCallback(() => {
    configureProject({ project_id: projectID as string });
  }, [configureProject, projectID]);

  React.useEffect(() => {
    if (isConfiguringProject) {
      updateProjectStatus("configuring");
    }
  }, [isConfiguringProject, updateProjectStatus]);

  React.useEffect(() => {
    const values = Object.values(jobStatus);

    // It should be 2.
    if (values.length !== 2) {
      setCanConfigureProject(false);
      return;
    }

    // All them should be success
    for (const val of values) {
      if (val !== "success") {
        setCanConfigureProject(false);
        return;
      }
    }

    setCanConfigureProject(true);
  }, [jobStatus]);

  return (
    <ActionButton
      message="Configure this project"
      size="default"
      variant="default"
      icon={<PlayIcon />}
      isLoading={isConfiguringProject}
      disabled={!canConfigureProject || isConfiguringProject}
      onClick={handleOnConfigureProject}
    >
      Configure Project
    </ActionButton>
  );
}
