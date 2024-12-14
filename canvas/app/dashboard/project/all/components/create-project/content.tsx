"use client";

import { Modal } from "@/components/custom/modal";
import { CreateProjectForm } from "./form";
import { Button } from "@/components/ui/button";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import {
  createProject,
  GET_PROJECT_QUERY_KEY,
  TProject,
} from "@/services/projects";
import { useRouter } from "next/navigation";
import React from "react";
import { TCreateProjectFormData } from "@/schema/create-project";
import { Alert } from "@/components/custom/alert";
import { PROJECT_URL } from "@/constants/routes";

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
        queryKey: [GET_PROJECT_QUERY_KEY],
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
      createNewProject(data);
    },
    [createNewProject]
  );

  return (
    <Modal
      title="Create a new project"
      trigger={<Button>Create Project</Button>}
      hasCloseButtonInFooter
      actions={[
        <Button key="create" className="my-1" type="submit" form={formID}>
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
