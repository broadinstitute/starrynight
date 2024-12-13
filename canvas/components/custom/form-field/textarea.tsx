import { Textarea, TextareaProps } from "@/components/ui/textarea";
import { BaseFormField, TBaseFormFieldProps } from "./_base";
import clsx from "clsx";
import { FieldPath, FieldValues } from "react-hook-form";

export type TTextAreaFormField<
  TFieldValues extends FieldValues = FieldValues,
  TName extends FieldPath<TFieldValues> = FieldPath<TFieldValues>
> = Omit<TBaseFormFieldProps<TFieldValues, TName>, "render"> & {
  textAreaProps?: TextareaProps;
};

export function TextAreaFormField<
  TFieldValues extends FieldValues = FieldValues,
  TName extends FieldPath<TFieldValues> = FieldPath<TFieldValues>
>(props: TTextAreaFormField<TFieldValues, TName>) {
  const { textAreaProps = {}, ...rest } = props;
  const { className, ...textAreaRest } = textAreaProps;
  return (
    <BaseFormField
      {...rest}
      render={({ field }) => {
        return (
          <Textarea
            {...textAreaRest}
            className={clsx("resize-none", className)}
            {...field}
          />
        );
      }}
    />
  );
}
