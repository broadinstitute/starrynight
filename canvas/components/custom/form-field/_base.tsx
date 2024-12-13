import React from "react";
import { ControllerProps, FieldPath, FieldValues } from "react-hook-form";

import {
  FormField,
  FormItem,
  FormLabel,
  FormControl,
  FormDescription,
  FormMessage,
} from "@/components/ui/form";

export type TBaseFormFieldProps<
  TFieldValues extends FieldValues = FieldValues,
  TName extends FieldPath<TFieldValues> = FieldPath<TFieldValues>
> = ControllerProps<TFieldValues, TName> & {
  description?: string;
  label: string;
};

export function BaseFormField<
  TFieldValues extends FieldValues = FieldValues,
  TName extends FieldPath<TFieldValues> = FieldPath<TFieldValues>
>(props: TBaseFormFieldProps<TFieldValues, TName>) {
  const { description, label, render, ...rest } = props;

  return (
    <FormField
      {...rest}
      render={(renderProps) => (
        <FormItem>
          <FormLabel>{label}</FormLabel>
          <FormControl>{render(renderProps)}</FormControl>
          {description && <FormDescription>{description}</FormDescription>}
          <FormMessage />
        </FormItem>
      )}
    />
  );
}
