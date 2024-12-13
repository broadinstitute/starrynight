import { Input, InputProps } from "@/components/ui/input";
import { BaseFormField, TBaseFormFieldProps } from "./_base";
import { FieldPath, FieldValues } from "react-hook-form";

export type TInputFormField<
  TFieldValues extends FieldValues = FieldValues,
  TName extends FieldPath<TFieldValues> = FieldPath<TFieldValues>
> = Omit<TBaseFormFieldProps<TFieldValues, TName>, "render"> & {
  inputProps?: InputProps;
};

export function InputFormField<
  TFieldValues extends FieldValues = FieldValues,
  TName extends FieldPath<TFieldValues> = FieldPath<TFieldValues>
>(props: TInputFormField<TFieldValues, TName>) {
  const { inputProps, ...rest } = props;
  return (
    <BaseFormField
      {...rest}
      render={({ field }) => {
        return <Input {...inputProps} {...field} />;
      }}
    />
  );
}
