"use client";

import React, { useMemo } from "react";

import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { Form, FormItem, FormLabel } from "@/components/ui/form";
import {
  TCreateProjectFormData,
  createProjectSchema,
} from "@/schema/create-project";
import { useGetParserAndProjectType } from "@/services/projects";
import { TextAreaFormField } from "@/components/custom/form-field/textarea";
import { InputFormField } from "@/components/custom/form-field/input";
import { SelectFormField } from "@/components/custom/form-field/select";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/services/api";
import { Input } from "@/components/ui/input";

export type TCreateProjectFormProps = {
  formID: string;
  onSubmit: (data: TCreateProjectFormData) => void;
  isSubmitting: boolean;
};

export function CreateProjectForm(props: TCreateProjectFormProps) {
  const { data, isLoading, error } = useGetParserAndProjectType({
    enabled: true,
  });

  const [parsers, types] = useMemo(() => {
    if (!data) return [[], []];

    const _parsers = data[0];
    const _types = data[1];

    const mapFn = (d: string) => ({ label: d, value: d });

    return [_parsers.map(mapFn), _types.map(mapFn)];
  }, [data]);

  const { formID, isSubmitting, onSubmit } = props;

  const { getValues, control, ...rest } = useForm<TCreateProjectFormData>({
    resolver: zodResolver(createProjectSchema),
    defaultValues: {
      name: "",
      description: "",
      dataset: "",
      workspaceURI: "",
      storageURI: "",
      isConfigured: false,
    },
  });

  const projectType = getValues("type");

  const handleUpdateInitConfig = React.useCallback(
    (key: string, value: string) => {
      rest.setValue("init_config", {
        ...getValues("init_config"),
        [key]: value,
      });
    },
    [rest, getValues]
  );

  // TODO: Fix why handleSubmit doesn't pass init_config value to onSubmit.
  // TODO: Could be related to how useForm handles nested objects in the form.
  const _onSubmit = React.useCallback(
    (data: TCreateProjectFormData) => {
      const init_config = getValues("init_config");

      onSubmit({
        ...data,
        init_config,
      });
    },
    [getValues, onSubmit]
  );

  // TODO: Move this to services.
  const { data: projectTypeConfig } = useQuery({
    queryKey: ["GET_INIT_CONFIG_KEY", projectType],
    queryFn: (): Promise<Record<string, Record<"title", string>>> =>
      api.get(`/project/type/${projectType}`).json(),
    enabled: !!projectType,
  });

  return (
    <Form getValues={getValues} control={control} {...rest}>
      <form
        onSubmit={rest.handleSubmit(_onSubmit)}
        className="space-y-4 text-left"
        id={formID}
      >
        {/* Project Name */}
        <InputFormField
          control={control}
          name="name"
          label="Name"
          inputProps={{
            placeholder: "Project Name",
            disabled: isSubmitting,
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
          }}
          description="Optional."
        />

        {/* Parser */}
        <SelectFormField
          control={control}
          name="parser"
          description="The parser to use to build the project."
          label="Parser"
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

        {projectTypeConfig &&
          Object.entries(projectTypeConfig).map(([key, value]) => (
            <FormItem key={key}>
              <FormLabel>{value.title}</FormLabel>
              <Input
                onChange={(e) =>
                  handleUpdateInitConfig(key, e.currentTarget.value)
                }
              />
            </FormItem>
          ))}
      </form>
    </Form>
  );
}
