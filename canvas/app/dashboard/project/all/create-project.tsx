"use client";

import React from "react";
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
import { ExclamationTriangleIcon, ReloadIcon } from "@radix-ui/react-icons";
import { CheckCircle } from "lucide-react";

const formID = "create-project-form";

export function CreateProject() {
  const [hasError, setHasError] = React.useState(false);
  const [isSubmitting, setIsSubmitting] = React.useState(false);
  const [isSuccess, setIsSuccess] = React.useState(false);

  const ref = React.useRef(0);

  const datasets = [
    {
      label: "Dataset 1",
      value: "d1",
    },
    {
      label: "Dataset 2",
      value: "d2",
    },
    {
      label: "Dataset 3",
      value: "d3",
    },
  ];

  const parser = [
    {
      label: "Parser 1",
      value: "p1",
    },
    {
      label: "Parser 2",
      value: "p2",
    },
    {
      label: "Parser 3",
      value: "p3",
    },
  ];

  function handleSubmit(data: TCreateProjectFormData) {
    setHasError(false);
    setIsSubmitting(false);
    setIsSuccess(false);
    console.log("Data", data);

    if (ref.current % 2 === 0) {
      setIsSubmitting(true);
      setTimeout(() => {
        setIsSubmitting(false);
        setIsSuccess(true);
      }, 1000);
      ref.current += 1;
    } else {
      setHasError(true);
      ref.current += 1;
    }
  }

  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button>Create Project</Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="mb-2 text-left">
            Create a new project
          </DialogTitle>
          {hasError && (
            <Alert variant="destructive">
              <ExclamationTriangleIcon className="h-4 w-4" />
              <AlertTitle>Error!</AlertTitle>
              <AlertDescription>
                Something went wrong while creating the project. Please try
                again after sometime.
              </AlertDescription>
            </Alert>
          )}
          {isSuccess && (
            <Alert variant="default">
              <CheckCircle className="h-4 w-4" />
              <AlertTitle>Success!</AlertTitle>
              <AlertDescription>Project created successfully.</AlertDescription>
            </Alert>
          )}
          <CreateProjectForm
            datasets={datasets}
            parsers={parser}
            onSubmit={handleSubmit}
            formID={formID}
          />
        </DialogHeader>
        <DialogFooter className="sm:justify-start md:justify-between">
          <DialogClose asChild>
            <Button
              type="button"
              className="my-1"
              variant="secondary"
              disabled={isSubmitting}
            >
              Close
            </Button>
          </DialogClose>
          <Button
            className="my-1"
            type="submit"
            form={formID}
            disabled={isSubmitting}
          >
            {isSubmitting && (
              <ReloadIcon className="mr-2 h-4 w-4 animate-spin" />
            )}
            Create
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
