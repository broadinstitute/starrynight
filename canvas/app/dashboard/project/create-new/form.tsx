"use client";

import React from "react";
import { withCreateNewProjectProvider } from "./provider";
import { CreateNewProjectStep1 } from "./step-1";
import { useCreateNewProjectStore } from "./store";
import { CreateNewProjectStep2 } from "./step-2";
import { CreateNewProjectCounter } from "./counter";
import { Form } from "@/components/ui/form";
import { zodResolver } from "@hookform/resolvers/zod";
import {
  createProjectSchema,
  TCreateProjectFormData,
} from "@/schema/create-project";
import { useForm } from "react-hook-form";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import {
  createProject,
  GET_PROJECTS_QUERY_KEY,
  TProject,
} from "@/services/projects";
import { Alert } from "@/components/custom/alert";
import { useRouter } from "next/navigation";
import { PROJECT_URL } from "@/constants/routes";

function CreateNewProjectForm_() {
  const { currentStep, updateCurrentStep, updateIsFormSubmitting } =
    useCreateNewProjectStore((store) => ({
      currentStep: store.currentStep,
      updateCurrentStep: store.updateCurrentStep,
      updateIsFormSubmitting: store.updateIsFormSubmitting,
    }));

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

  const handleOnCreateProjectError = React.useCallback(() => {
    updateIsFormSubmitting(false);
    updateCurrentStep(0);
  }, [updateCurrentStep, updateIsFormSubmitting]);

  const form = useForm<TCreateProjectFormData>({
    resolver: zodResolver(createProjectSchema),
    defaultValues: {
      name: "",
      description: "",
      dataset: "",
      workspaceURI: "",
      storageURI: "",
      init_config: [],
    },
  });

  const {
    isError: hasErrorDuringCreatingProject,
    isSuccess: hasCreatedProjectSuccessfully,
    mutate: createNewProject,
  } = useMutation({
    mutationFn: createProject,
    onSuccess: handleOnCreateProjectSuccess,
    onError: handleOnCreateProjectError,
  });

  const handleOnFormSubmit = React.useCallback(
    (data: TCreateProjectFormData) => {
      const {
        dataset,
        storageURI,
        workspaceURI,
        description,
        name,
        parser,
        type,
        init_config,
      } = data;

      updateIsFormSubmitting(true);
      createNewProject({
        dataset_uri: dataset,
        storage_uri: storageURI || dataset,
        workspace_uri: workspaceURI || dataset,
        description: description || "",
        name,
        parser_type: parser,
        type,
        init_config: Object.fromEntries(init_config),
        is_configured: false,
      });
    },
    [createNewProject, updateIsFormSubmitting]
  );

  const Steps = React.useMemo(
    (): Record<number, React.ReactNode> => ({
      0: <CreateNewProjectStep1 />,
      1: <CreateNewProjectStep2 />,
    }),
    []
  );

  return (
    <div className="flex">
      <div className="hidden px-12 md:block">
        <CreateNewProjectCounter />
      </div>
      <div className="pl-12 flex-1 max-w-md space-y-4">
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

        <Form {...form}>
          <form
            className="w-full max-w-md"
            onSubmit={form.handleSubmit(handleOnFormSubmit)}
          >
            {Steps[currentStep]}
          </form>
        </Form>
      </div>
    </div>
  );
}

const CreateNewProjectForm = withCreateNewProjectProvider(
  CreateNewProjectForm_
);

export { CreateNewProjectForm };
