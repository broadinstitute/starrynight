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
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import {
  TCreateProjectFormData,
  createProjectSchema,
} from "@/schema/create-project";

export type TCreateProjectFormProps = {
  formID: string;
  onSubmit: (data: TCreateProjectFormData) => void;
  parsers: string[];
  type: string[];
  isSubmitting: boolean;
};

export function CreateProjectForm(props: TCreateProjectFormProps) {
  const { formID, parsers, type, isSubmitting, onSubmit } = props;

  const createProjectForm = useForm<TCreateProjectFormData>({
    resolver: zodResolver(createProjectSchema),
    defaultValues: {
      name: "",
      description: "",
      dataset: "",
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
        <FormField
          control={createProjectForm.control}
          name="name"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Name</FormLabel>
              <FormControl>
                <Input
                  {...field}
                  placeholder="Project Name"
                  disabled={isSubmitting}
                />
              </FormControl>
              <FormDescription>The name of the project.</FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />

        {/* Description */}
        <FormField
          control={createProjectForm.control}
          name="description"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Description</FormLabel>
              <FormControl>
                <Textarea
                  disabled={isSubmitting}
                  placeholder="Description"
                  className="resize-none"
                  {...field}
                />
              </FormControl>
              <FormDescription>
                The description of the project. It should not exceed 100
                characters.
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />

        {/* Dataset */}
        <FormField
          control={createProjectForm.control}
          name="dataset"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Dataset</FormLabel>
              <FormControl>
                <Input
                  {...field}
                  placeholder="Dataset"
                  disabled={isSubmitting}
                />
              </FormControl>
              <FormDescription>
                S3 bucket URL that contains the dataset.
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />

        {/* Parser */}
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
                  disabled={isSubmitting}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select Parser" />
                  </SelectTrigger>
                  <SelectContent onBlur={field.onBlur}>
                    {parsers.map((parser) => (
                      <SelectItem key={parser} value={parser}>
                        {parser}
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

        {/* Type */}
        <FormField
          control={createProjectForm.control}
          name="type"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Project Type</FormLabel>
              <FormControl>
                <Select
                  onValueChange={field.onChange}
                  defaultValue={field.value}
                  disabled={isSubmitting}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select Project Type" />
                  </SelectTrigger>
                  <SelectContent onBlur={field.onBlur}>
                    {type.map((type) => (
                      <SelectItem key={type} value={type}>
                        {type}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </FormControl>
              <FormDescription>The type of the project.</FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />
      </form>
    </Form>
  );
}
