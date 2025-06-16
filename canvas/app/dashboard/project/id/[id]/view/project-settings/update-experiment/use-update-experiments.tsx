import React from "react";
import { useToast } from "@/components/ui/use-toast";
import {
  TProject,
  TProjectExperiment,
  useConfigureProject,
  useUpdateProject,
} from "@/services/projects";
import { useProjectStore } from "@/stores/project";

export type TUseUpdateExperiemntsOptions = {
  onSuccess: () => void;
};

export function useUpdateExperiments(options: TUseUpdateExperiemntsOptions) {
  const { onSuccess } = options;
  const [isPending, setIsPending] = React.useState(false);
  const { toast } = useToast();

  const project = useProjectStore((store) => store.project);

  const handleOnConfigureProjectSuccess = React.useCallback(() => {
    setIsPending(false);
    toast({
      variant: "default",
      title: "Project's experiment updated successfully!",
    });
    onSuccess;
  }, [toast, onSuccess]);

  const handleOnConfigureProjectError = React.useCallback(() => {
    setIsPending(false);
    toast({
      variant: "destructive",
      title: "Failed to configure project",
      description:
        "Project's experiment was updated, but failed to re-configure the project. Please try again.",
    });
  }, [toast]);

  const { mutate: configureProject } = useConfigureProject({
    onSuccess: handleOnConfigureProjectSuccess,
    onError: handleOnConfigureProjectError,
  });

  const handleOnUpdateProjectSuccess = React.useCallback(
    (data: TProject) => {
      configureProject({
        project_id: data.id,
      });
    },
    [configureProject],
  );

  const handleOnUpdateProjectError = React.useCallback(() => {
    toast({
      variant: "destructive",
      title: "Failed to update project's experiments",
    });
    setIsPending(false);
  }, [toast]);

  const { mutate: updateProject } = useUpdateProject({
    onError: handleOnUpdateProjectError,
    onSuccess: handleOnUpdateProjectSuccess,
  });

  const updateExperiments = React.useCallback(
    (experiments: TProjectExperiment) => {
      setIsPending(true);
      updateProject({
        project: {
          ...project,
          experiment: {
            ...experiments,
            init_config: {},
          },
        },
      });
    },
    [updateProject, project],
  );

  return {
    isPending,
    updateExperiments,
  };
}
