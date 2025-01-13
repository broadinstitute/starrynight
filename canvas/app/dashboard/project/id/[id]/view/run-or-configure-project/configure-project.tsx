import React from "react";

import { ActionButton } from "@/components/custom/action-button";
import { useToast } from "@/components/ui/use-toast";
import { GET_JOBS_QUERY_KEY } from "@/services/job";
import {
  GET_PROJECT_QUERY_KEY,
  useConfigureProject,
} from "@/services/projects";
import { GET_RUNS_QUERY_KEY } from "@/services/run";
import { useProjectStore } from "@/stores/project";
import { useQueryClient } from "@tanstack/react-query";
import { Settings } from "lucide-react";

export function ProjectConfigureProject() {
  const queryClient = useQueryClient();

  const { projectID, jobStatus, updateProjectStatus } = useProjectStore(
    (store) => ({
      projectID: store.project.id,
      jobStatus: store.jobStatus,
      updateProjectStatus: store.updateProjectStatus,
    })
  );

  const { toast } = useToast();

  const handleOnConfigureProjectSuccess = React.useCallback(async () => {
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

    updateProjectStatus("configured");
    toast({
      title: "Project configured successfully!",
      variant: "default",
    });
  }, [toast, updateProjectStatus, queryClient]);

  const handleOnConfigureProjectError = React.useCallback(() => {
    toast({
      title: "Error configuring the project!",
      variant: "destructive",
    });

    updateProjectStatus("not-configured");
  }, [toast]);

  const { mutate: configureProject, isPending: isConfiguringProject } =
    useConfigureProject({
      onSuccess: handleOnConfigureProjectSuccess,
      onError: handleOnConfigureProjectError,
    });

  const [canConfigureProject, setCanConfigureProject] = React.useState(false);

  const handleOnConfigureProject = React.useCallback(() => {
    configureProject({ project_id: projectID as string });
  }, []);

  React.useEffect(() => {
    if (isConfiguringProject) {
      updateProjectStatus("configuring");
    }
  }, []);

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
      icon={<Settings />}
      isLoading={isConfiguringProject}
      disabled={!canConfigureProject || isConfiguringProject}
      onClick={handleOnConfigureProject}
    >
      Configure Project
    </ActionButton>
  );
}
