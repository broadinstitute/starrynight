import { Button } from "@/components/ui/button";
import { ChevronLeft, Loader2 } from "lucide-react";
import React from "react";
import { useCreateNewProjectStore } from "./store";
import { useFieldArray, useFormContext } from "react-hook-form";
import { TCreateProjectFormData } from "@/schema/create-project";
import { useGetProjectInitConfigUsingProjectType } from "@/services/projects";
import { PageSpinner } from "@/components/custom/page-spinner";
import { FormItem, FormLabel } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import clsx from "clsx";

export function CreateNewProjectStep2() {
  const { currentStep, isFormSubmitting, updateCurrentStep } =
    useCreateNewProjectStore((store) => ({
      currentStep: store.currentStep,
      isFormSubmitting: store.isFormSubmitting,
      updateCurrentStep: store.updateCurrentStep,
    }));

  const { getValues, control, register } =
    useFormContext<TCreateProjectFormData>();
  const projectType = getValues("type");

  const { data, error, isLoading } = useGetProjectInitConfigUsingProjectType({
    project_type: projectType,
  });

  const { fields, append, remove } = useFieldArray({
    control,
    name: "init_config",
  });

  React.useEffect(() => {
    if (data) {
      remove();
      Object.entries(data).forEach(([key, val]) => {
        append([[key, "", val]]);
      });
    }
  }, [data, currentStep]);

  const handleOnBackClick = React.useCallback(() => {
    updateCurrentStep(currentStep - 1);
  }, [currentStep, updateCurrentStep]);

  if (isLoading) {
    return (
      <div className="w-96 flex justify-center items-center">
        <PageSpinner />
      </div>
    );
  }

  if (!data || error) {
    return (
      <div>
        <p className="max-w-md text-sm text-destructive">
          Error fetching project init config for {projectType}. Please try again
          later.
        </p>
        <div className="flex justify-between mt-12">
          <Button variant="secondary" onClick={handleOnBackClick}>
            <ChevronLeft />
            Back
          </Button>
        </div>
      </div>
    );
  }

  if (fields.length === 0) {
    return (
      <div>
        <p className="max-w-md text-sm text-gray-600">
          Project type "{projectType}" requires no config to initialize the
          project. Click the "Create project" button to create the project. If
          you want to change the project type press "Back"
        </p>
        <div className="flex justify-between mt-12">
          <Button variant="secondary" onClick={handleOnBackClick}>
            <ChevronLeft />
            Back
          </Button>
          <Button>Create project</Button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-md space-y-4 text-left">
      {fields.map((field, index) => (
        <FormItem key={field.id}>
          <FormLabel>{field[2].title || field[0]}</FormLabel>
          <Input {...register(`init_config.${index}.1`)} />
        </FormItem>
      ))}
      <div className="flex justify-between pt-4">
        <Button
          disabled={isFormSubmitting}
          variant="secondary"
          onClick={handleOnBackClick}
        >
          <ChevronLeft />
          Back
        </Button>
        <Button disabled={isFormSubmitting}>
          {isFormSubmitting ? (
            <Loader2 className={clsx("animate-spin")} />
          ) : null}
          Create project
        </Button>
      </div>
    </div>
  );
}
