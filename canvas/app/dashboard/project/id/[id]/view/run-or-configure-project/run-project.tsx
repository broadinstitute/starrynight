import { ActionButton } from "@/components/custom/action-button";
import { useToast } from "@/components/ui/use-toast";
import { useExecuteProject } from "@/services/projects";
import { useProjectStore } from "@/stores/project";
import { PlayIcon } from "lucide-react";
import React from "react";

export function ProjectRunProject() {
  const { projectID, projectStatus, updateProjectStatus } = useProjectStore(
    (store) => ({
      projectID: store.project.id,
      projectStatus: store.projectStatus,
      updateProjectStatus: store.updateProjectStatus,
    }),
  );

  const { toast } = useToast();

  const handleOnExecuteProjectSuccessful = React.useCallback(async () => {
    toast({
      title: "Project started successfully!",
      variant: "default",
    });
  }, [toast]);

  const handleOnExecuteProjectError = React.useCallback(() => {
    toast({
      title: "Error executing the project",
      variant: "destructive",
    });

    updateProjectStatus("configured");
  }, [toast, updateProjectStatus]);

  const { mutate: executeProject, isPending } = useExecuteProject({
    onError: handleOnExecuteProjectError,
    onSuccess: handleOnExecuteProjectSuccessful,
  });

  const handleOnClickRunProject = React.useCallback(() => {
    executeProject({
      project_id: projectID,
    });
  }, [projectID, executeProject]);

  return (
    <ActionButton
      size="default"
      variant="default"
      icon={<PlayIcon />}
      message="Run project"
      disabled={isPending}
      isLoading={isPending}
      onClick={handleOnClickRunProject}
    >
      Run Project
    </ActionButton>
  );
}
