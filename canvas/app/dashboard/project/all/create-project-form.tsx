"use client";

import React from "react";

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
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  TCreateProjectFormData,
  createProjectSchema,
} from "@/schema/create-project";

type TSelectObject = {
  label: string;
  value: string;
};

export type TCreateProjectFormProps = {
  formID: string;
  onSubmit: (data: TCreateProjectFormData) => void;
  parsers: TSelectObject[];
  datasets: TSelectObject[];
};

export function CreateProjectForm(props: TCreateProjectFormProps) {
  const { formID, datasets, parsers, onSubmit } = props;

  const createProjectForm = useForm<TCreateProjectFormData>({
    resolver: zodResolver(createProjectSchema),
  });

  return (
    <Form {...createProjectForm}>
      <form
        onSubmit={createProjectForm.handleSubmit(onSubmit)}
        className="space-y-4 text-left"
        id={formID}
      >
        <FormField
          control={createProjectForm.control}
          name="dataset"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Dataset</FormLabel>
              <FormControl>
                <Select
                  onValueChange={field.onChange}
                  defaultValue={field.value}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select Dataset" />
                  </SelectTrigger>
                  <SelectContent onBlur={field.onBlur}>
                    {datasets.map(({ value, label }) => (
                      <SelectItem key={value} value={value}>
                        {label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </FormControl>
              <FormDescription>
                The dataset to use to build the project.
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={createProjectForm.control}
          name="parser"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Parser</FormLabel>
              <FormControl>
                <Select
                  onValueChange={field.onChange}
                  defaultValue={field.value}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select Parser" />
                  </SelectTrigger>
                  <SelectContent onBlur={field.onBlur}>
                    {parsers.map(({ value, label }) => (
                      <SelectItem key={value} value={value}>
                        {label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </FormControl>
              <FormDescription>
                The parser to use to build the project.
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />
      </form>
    </Form>
  );
}
