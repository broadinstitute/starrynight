"use client";

import React from "react";
import useSWR from "swr";
import {
  Dialog,
  DialogContent,
  DialogTrigger,
  DialogHeader,
  DialogTitle,
  DialogClose,
  DialogFooter,
} from "@/components/ui/dialog";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";

import { Button } from "@/components/ui/button";
import { CreateProjectForm } from "./create-project-form";
import { TCreateProjectFormData } from "@/schema/create-project";
import { ExclamationTriangleIcon } from "@radix-ui/react-icons";
import { CheckCircle, Loader2 } from "lucide-react";
import { createProject, getParserAndProjectType } from "@/services/projects";
import { useMutation } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { PROJECT_URL } from "@/constants/routes";

const formID = "create-project-form";

export function CreateProject() {
  const { push } = useRouter();
  const { data, isLoading: isLoadingParserAndProjectType } = useSWR(
    "getParserAndType",
    getParserAndProjectType,
    {
      revalidateIfStale: false,
      revalidateOnFocus: false,
      revalidateOnReconnect: false,
    }
  );

  const {
    isError: hasErrorDuringCreatingProject,
    isSuccess: hasCreatedProjectSuccessfully,
    isPending: isSubmittingCreateProjectForm,
    data: createNewProjectResponse,
    mutate: createNewProject,
  } = useMutation({
    mutationFn: createProject,
  });

  function handleSubmit(data: TCreateProjectFormData) {
    createNewProject(data);
  }

  const isErrorLoadingParserAndProjectType = !data || !!data.error;
  const hasParserAndProjectType = data && data.response;

  React.useEffect(() => {
    if (createNewProjectResponse) {
      setTimeout(() => {
        push(`${PROJECT_URL}/${createNewProjectResponse.id}`);
      }, 3000);
    }
  }, [createNewProjectResponse, push]);

  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button>Create Project</Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-md max-h-full overflow-auto">
        <DialogHeader>
          <DialogTitle className="mb-2 text-left">
            Create a new project
          </DialogTitle>
          {hasErrorDuringCreatingProject && (
            <Alert variant="destructive">
              <ExclamationTriangleIcon className="h-4 w-4" />
              <AlertTitle>Error!</AlertTitle>
              <AlertDescription>
                Something went wrong while creating the project. Please try
                again after sometime.
              </AlertDescription>
            </Alert>
          )}
          {hasCreatedProjectSuccessfully && (
            <Alert variant="default">
              <CheckCircle className="h-4 w-4" />
              <AlertTitle>Success!</AlertTitle>
              <AlertDescription>Project created successfully.</AlertDescription>
            </Alert>
          )}

          {isLoadingParserAndProjectType && (
            <div className="p-8 flex justify-center items-center">
              <Loader2 className="animate-spin" />
            </div>
          )}

          {isErrorLoadingParserAndProjectType && (
            <div className="py-8">
              Something went wrong! Please try again later.
            </div>
          )}

          {hasParserAndProjectType && (
            <CreateProjectForm
              parsers={data.response![0]}
              type={data.response![1]}
              onSubmit={handleSubmit}
              formID={formID}
              isSubmitting={isSubmittingCreateProjectForm}
            />
          )}
        </DialogHeader>
        {hasParserAndProjectType && (
          <DialogFooter className="sm:justify-start md:justify-between">
            <DialogClose asChild>
              <Button
                type="button"
                className="my-1"
                variant="secondary"
                disabled={isSubmittingCreateProjectForm}
              >
                Close
              </Button>
            </DialogClose>
            <Button
              className="my-1"
              type="submit"
              form={formID}
              disabled={isSubmittingCreateProjectForm}
            >
              {isSubmittingCreateProjectForm && (
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              )}
              Create
            </Button>
          </DialogFooter>
        )}
      </DialogContent>
    </Dialog>
  );
}
