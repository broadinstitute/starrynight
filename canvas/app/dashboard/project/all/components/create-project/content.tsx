"use client";

import { Modal } from "@/components/custom/modal";
import { CreateProjectForm } from "./form";
import { Button } from "@/components/ui/button";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import {
  createProject,
  GET_PROJECTS_QUERY_KEY,
  TProject,
} from "@/services/projects";
import { useRouter } from "next/navigation";
import React from "react";
import { TCreateProjectFormData } from "@/schema/create-project";
import { Alert } from "@/components/custom/alert";
import { PROJECT_URL } from "@/constants/routes";
import { Loader2 } from "lucide-react";

const formID = "create-project-form";

export function CreateProjectContent() {
  const { push } = useRouter();
  const queryClient = useQueryClient();

  const handleOnCreateProjectSuccess = React.useCallback(
    async (data: TProject) => {
      /**
       * Invalidating queries, as after creating new
       * project we want to fetch it.
       */
      await queryClient.invalidateQueries({
        queryKey: [GET_PROJECTS_QUERY_KEY],
      });

      setTimeout(() => {
        push(`${PROJECT_URL}/${data.id}`);
      }, 3000);
    },
    [push, queryClient]
  );

  const {
    isError: hasErrorDuringCreatingProject,
    isSuccess: hasCreatedProjectSuccessfully,
    isPending: isSubmittingCreateProjectForm,
    mutate: createNewProject,
  } = useMutation({
    mutationFn: createProject,
    onSuccess: handleOnCreateProjectSuccess,
  });

  const handleSubmit = React.useCallback(
    (data: TCreateProjectFormData) => {
      const {
        dataset,
        storageURI,
        workspaceURI,
        description,
        isConfigured,
        name,
        parser,
        type,
        init_config,
      } = data;

      createNewProject({
        dataset_uri: dataset,
        storage_uri: storageURI || dataset,
        workspace_uri: workspaceURI || dataset,
        description: description || "",
        is_configured: isConfigured,
        name,
        parser_type: parser,
        type,
        init_config,
      });
    },
    [createNewProject]
  );

  return (
    <Modal
      title="Create a new project"
      trigger={<Button>Create Project</Button>}
      hasCloseButtonInFooter
      actions={[
        <Button
          disabled={isSubmittingCreateProjectForm}
          key="create"
          className="my-1"
          type="submit"
          form={formID}
        >
          {isSubmittingCreateProjectForm && (
            <Loader2 className="animate-spin" />
          )}
          Create
        </Button>,
      ]}
    >
      {hasErrorDuringCreatingProject && (
        <Alert
          variant="destructive"
          title="Error!"
          description=" Something went wrong while creating the project. Please try again after sometime."
        />
      )}

      {hasCreatedProjectSuccessfully && (
        <Alert
          variant="default"
          title="Success!"
          description="Project created successfully."
        />
      )}

      <CreateProjectForm
        onSubmit={handleSubmit}
        formID={formID}
        isSubmitting={isSubmittingCreateProjectForm}
      />
    </Modal>
  );
}
