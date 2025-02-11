import { ActionButton } from "@/components/custom/action-button";
import { Modal, ModalCloseTrigger } from "@/components/custom/modal";
import { Button } from "@/components/ui/button";
import { useToast } from "@/components/ui/use-toast";
import { PROJECTS_LISTING_URL } from "@/constants/routes";
import {
  GET_PROJECT_QUERY_KEY,
  GET_PROJECTS_QUERY_KEY,
  useDeleteProject,
} from "@/services/projects";
import { useProjectStore } from "@/stores/project";
import { useQueryClient } from "@tanstack/react-query";
import { Trash2 } from "lucide-react";
import { useRouter } from "next/navigation";
import React from "react";

export function ProjectDeleteAction() {
  const [isDeleteInProgress, setIsDeleteInProgress] = React.useState(false);

  const { project } = useProjectStore((store) => ({
    project: store.project,
  }));

  const { toast } = useToast();
  const router = useRouter();
  const queryClient = useQueryClient();

  const handleOnSuccessDeletingProject = React.useCallback(async () => {
    toast({
      variant: "default",
      title: "Project deleted successfully.",
    });

    // Invalidating all projects and current project query.
    await Promise.all([
      queryClient.invalidateQueries({
        queryKey: [GET_PROJECTS_QUERY_KEY],
      }),
      queryClient.invalidateQueries({
        queryKey: [GET_PROJECT_QUERY_KEY, project.id],
      }),
    ]);

    router.push(PROJECTS_LISTING_URL);
  }, [toast, router, project, queryClient]);

  const handleOnErrorDeletingProject = React.useCallback(() => {
    toast({
      variant: "destructive",
      title: "Failed to delete project. Please try again.",
    });
    setIsDeleteInProgress(false);
  }, [toast]);

  const { mutate: deleteProject } = useDeleteProject({
    onError: handleOnErrorDeletingProject,
    onSuccess: handleOnSuccessDeletingProject,
  });

  const handleOnDeleteRequest = React.useCallback(() => {
    setIsDeleteInProgress(true);
    deleteProject({ project_id: project.id });
  }, [project, deleteProject]);

  return (
    <Modal
      title="Are you sure?"
      headerIcon={<Trash2 />}
      hasCloseButtonInFooter
      trigger={
        <ActionButton
          isLoading={isDeleteInProgress}
          size="default"
          icon={<Trash2 />}
          variant="destructive"
          message="Delete project"
        >
          Delete Project
        </ActionButton>
      }
      actions={[
        <ModalCloseTrigger asChild key="delete">
          <Button onClick={handleOnDeleteRequest} variant="destructive">
            Delete
          </Button>
        </ModalCloseTrigger>,
      ]}
    >
      <p>
        This action cannot be undone. Deleting &nbsp;
        <b>&quot;{project.name}&quot;</b>&nbsp; will remove all associated data
        permanently. Please confirm that you want to proceed.
      </p>
    </Modal>
  );
}
