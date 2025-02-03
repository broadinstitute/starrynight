import { InputFormField } from "@/components/custom/form-field/input";
import { SelectFormField } from "@/components/custom/form-field/select";
import { useCreateNewProjectStore } from "./store";
import { TextAreaFormField } from "@/components/custom/form-field/textarea";
import { useGetParserAndProjectType } from "@/services/projects";
import React from "react";
import { Button } from "@/components/ui/button";
import { useFormContext } from "react-hook-form";
import {
  createProjectSchema,
  TCreateProjectFormData,
} from "@/schema/create-project";
import { ChevronRight } from "lucide-react";

export function CreateNewProjectStep1() {
  const { currentStep, isFormSubmitting, updateCurrentStep } =
    useCreateNewProjectStore((store) => ({
      currentStep: store.currentStep,
      isFormSubmitting: store.isFormSubmitting,
      updateCurrentStep: store.updateCurrentStep,
    }));

  const {
    trigger,
    getValues,
    control,
    formState: { isSubmitting },
  } = useFormContext();

  const { data, isLoading, error } = useGetParserAndProjectType({
    enabled: true,
  });

  const hasTriggerCalled = React.useRef(false);

  const [parsers, types] = React.useMemo(() => {
    if (!data) return [[], []];

    const _parsers = data[0];
    const _types = data[1];

    const mapFn = (d: string) => ({ label: d, value: d });

    return [_parsers.map(mapFn), _types.map(mapFn)];
  }, [data]);

  const handleOnClickNext = React.useCallback(async () => {
    const { success } = createProjectSchema.safeParse(getValues());

    if (success) {
      hasTriggerCalled.current = false;
      return updateCurrentStep(currentStep + 1);
    }

    const TRIGGER_VALIDATION_FOR: (keyof TCreateProjectFormData)[] = [
      "name",
      "description",
      "dataset",
      "workspaceURI",
      "storageURI",
      "parser",
      "type",
    ];

    TRIGGER_VALIDATION_FOR.forEach((key) => trigger(key));
    hasTriggerCalled.current = true;
  }, [currentStep, getValues, updateCurrentStep, trigger]);

  const handleTriggerValidation = React.useCallback(
    (name: keyof TCreateProjectFormData) => {
      if (!hasTriggerCalled.current) return;
      trigger(name);
    },
    [trigger]
  );

  return (
    <div className="max-w-md space-y-4 text-left">
      {/* Project Name */}
      <InputFormField
        control={control}
        name="name"
        label="Name"
        inputProps={{
          placeholder: "Project Name",
          disabled: isSubmitting,
          onChange: () => handleTriggerValidation("name"),
        }}
        description="The name of the project."
      />

      {/* Description */}
      <TextAreaFormField
        control={control}
        name="description"
        label="Description"
        textAreaProps={{
          disabled: isSubmitting,
          placeholder: "Description",
          onChange: () => handleTriggerValidation("description"),
        }}
        description="The description of the project. It should not exceed 100 characters."
      />

      {/* Dataset */}
      <InputFormField
        control={control}
        name="dataset"
        label="Dataset"
        inputProps={{
          placeholder: "Dataset",
          disabled: isSubmitting,
          onChange: () => handleTriggerValidation("dataset"),
        }}
        description="S3 bucket URL that contains the dataset."
      />

      {/* Workspace URI */}
      <InputFormField
        control={control}
        name="workspaceURI"
        label="Workspace"
        inputProps={{
          placeholder: "Workspace",
          disabled: isSubmitting,
          onChange: () => handleTriggerValidation("workspaceURI"),
        }}
        description="Optional"
      />

      {/* Storage URI */}
      <InputFormField
        control={control}
        name="storageURI"
        label="Storage URI"
        inputProps={{
          placeholder: "Storage URI",
          disabled: isSubmitting,
          onChange: () => handleTriggerValidation("storageURI"),
        }}
        description="Optional."
      />

      {/* Parser */}
      <SelectFormField
        control={control}
        name="parser"
        description="The parser to use to build the project."
        label="Parser"
        onChange={() => handleTriggerValidation("parser")}
        selectProps={{
          disabled: isSubmitting,
          placeholder: "Select Parser",
          noDataMsg: "No parser available.",
          errorMsg: "Unable to load parsers.",
          isLoading,
          data: parsers,
          error,
        }}
      />

      {/* Type */}
      <SelectFormField
        control={control}
        name="type"
        description="The type of the project."
        label="Project Type"
        onChange={() => handleTriggerValidation("type")}
        selectProps={{
          disabled: isSubmitting,
          placeholder: "Select Project Type",
          noDataMsg: "No project type available.",
          errorMsg: "Unable to load project type.",
          isLoading,
          data: types,
          error,
        }}
      />

      <div className="flex justify-end">
        <Button
          onClick={handleOnClickNext}
          disabled={isFormSubmitting}
          type="button"
        >
          Init Project
          <ChevronRight />
        </Button>
      </div>
    </div>
  );
}
