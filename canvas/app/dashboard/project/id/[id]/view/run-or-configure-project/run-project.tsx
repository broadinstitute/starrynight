import { ActionButton } from "@/components/custom/action-button";
import { useToast } from "@/components/ui/use-toast";
import { GET_JOBS_QUERY_KEY } from "@/services/job";
import { GET_PROJECT_QUERY_KEY, useExecuteProject } from "@/services/projects";
import { GET_RUNS_QUERY_KEY } from "@/services/run";
import { useProjectStore } from "@/stores/project";
import { useQueryClient } from "@tanstack/react-query";
import { PlayIcon } from "lucide-react";
import React from "react";

export function ProjectRunProject() {
  const { projectID, projectStatus, updateProjectStatus } = useProjectStore(
    (store) => ({
      projectID: store.project.id,
      projectStatus: store.projectStatus,
      updateProjectStatus: store.updateProjectStatus,
    })
  );

  const queryClient = useQueryClient();
  const { toast } = useToast();

  const handleOnExecuteProjectSuccessful = React.useCallback(async () => {
    const invalidateJobQuery = queryClient.invalidateQueries({
      queryKey: [GET_JOBS_QUERY_KEY],
    });

    const invalidateRunsQuery = queryClient.invalidateQueries({
      queryKey: [GET_RUNS_QUERY_KEY],
    });

    const invalidateProjectQuery = queryClient.invalidateQueries({
      queryKey: [GET_PROJECT_QUERY_KEY, projectID],
    });

    await Promise.all([
      invalidateJobQuery,
      invalidateRunsQuery,
      invalidateProjectQuery,
    ]);

    updateProjectStatus("running");

    toast({
      title: "Project configured successfully!",
      variant: "default",
    });
  }, [toast]);

  const handleOnExecuteProjectError = React.useCallback(() => {
    toast({
      title: "Error executing the project",
      variant: "destructive",
    });

    updateProjectStatus("configured");
  }, [toast]);

  const { data, isPending } = useExecuteProject({
    onError: handleOnExecuteProjectError,
    onSuccess: handleOnExecuteProjectSuccessful,
  });

  React.useEffect(() => {
    if (!data) return;
  }, [data]);

  return (
    <ActionButton
      size="default"
      variant="default"
      icon={<PlayIcon />}
      message="Run project"
      disabled={isPending || projectStatus === "running"}
      isLoading={isPending || projectStatus === "running"}
    >
      {projectStatus === "running" ? "Project is running" : "Run Project"}
    </ActionButton>
  );
}
