"use client";

import React, { useMemo } from "react";

import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectItemLoader,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  TCreateProjectFormData,
  createProjectSchema,
} from "@/schema/create-project";
import { useGetParserAndProjectType } from "@/services/projects";
import { TextAreaFormField } from "@/components/custom/form-field/textarea";
import { InputFormField } from "@/components/custom/form-field/input";
import { SelectFormField } from "@/components/custom/form-field/select";

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
    if (!data || !data.response || !data.ok) return [[], []];

    const _parsers = data.response[0];
    const _types = data.response[1];

    const mapFn = (d: string) => ({ label: d, value: d });

    return [_parsers.map(mapFn), _types.map(mapFn)];
  }, [data]);

  const { formID, isSubmitting, onSubmit } = props;

  const createProjectForm = useForm<TCreateProjectFormData>({
    resolver: zodResolver(createProjectSchema),
    defaultValues: {
      name: "",
      description: "",
      dataset: "",
      workspaceURI: "",
    },
  });

  return (
    <Form {...createProjectForm}>
      <form
        onSubmit={createProjectForm.handleSubmit(onSubmit)}
        className="space-y-4 text-left"
        id={formID}
      >
        {/* Project Name */}
        <InputFormField
          control={createProjectForm.control}
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
          control={createProjectForm.control}
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
          control={createProjectForm.control}
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
          control={createProjectForm.control}
          name="workspaceURI"
          label="Workspace"
          inputProps={{
            placeholder: "Workspace",
            disabled: isSubmitting,
          }}
          description="S3 Bucket URI for the workspace where you want to create this
                project."
        />

        {/* Parser */}
        <SelectFormField
          control={createProjectForm.control}
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
          control={createProjectForm.control}
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
      </form>
    </Form>
  );
}
