import {
  Select,
  SelectContent,
  SelectItem,
  SelectItemLoader,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { BaseFormField, TBaseFormFieldProps } from "./_base";
import { FieldPath, FieldValues } from "react-hook-form";

type TContentProps = {
  errorMsg: string;
  noDataMsg: string;
  data?: { label: string; value: string }[];
  error?: unknown;
  isLoading?: boolean;
};

export type TSelectField<
  TFieldValues extends FieldValues = FieldValues,
  TName extends FieldPath<TFieldValues> = FieldPath<TFieldValues>
> = Omit<TBaseFormFieldProps<TFieldValues, TName>, "render"> & {
  selectProps: {
    disabled: boolean;
    placeholder: string;
  } & TContentProps;
};

function Content(props: TContentProps) {
  const { data, error, errorMsg, noDataMsg, isLoading } = props;

  if (isLoading) {
    return <SelectItemLoader />;
  }

  if (!data || error) {
    return (
      <SelectItem disabled value="error">
        {errorMsg}
      </SelectItem>
    );
  }

  if (data.length === 0) {
    return (
      <SelectItem disabled value="no-data">
        {noDataMsg}
      </SelectItem>
    );
  }

  return (
    <>
      {data.map((item) => (
        <SelectItem key={item.value} value={item.value}>
          {item.label}
        </SelectItem>
      ))}
    </>
  );
}

export function SelectFormField<
  TFieldValues extends FieldValues = FieldValues,
  TName extends FieldPath<TFieldValues> = FieldPath<TFieldValues>
>(
  props: TSelectField<TFieldValues, TName> & {
    onChange?: (value: string) => void;
  }
) {
  const { selectProps, onChange, ...rest } = props;
  const { disabled, placeholder, ...selectPropsRest } = selectProps;

  return (
    <BaseFormField
      {...rest}
      render={({ field }) => {
        return (
          <Select
            onValueChange={(e) => {
              field.onChange(e);
              onChange?.(e);
            }}
            defaultValue={field.value}
            disabled={disabled}
          >
            <SelectTrigger>
              <SelectValue placeholder={placeholder} />
            </SelectTrigger>
            <SelectContent onBlur={field.onBlur}>
              <Content {...selectPropsRest} />
            </SelectContent>
          </Select>
        );
      }}
    />
  );
}
