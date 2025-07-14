import { InputTags } from "@/components/ui/input-tags";
import { Checkbox } from "@/components/ui/checkbox";
import { FormItem, FormLabel } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { TCreateProjectFormData } from "@/schema/create-project";
import {
  isProjectConfigStringField,
  isValidProjectConfigField,
  isProjectConfigNumberField,
  isProjectConfigBooleanField,
  isProjectConfigArrayField,
  isProjectConfigSelectField,
  isProjectConfigRadioField,
} from "@/utils/project-form";
import { Controller, useFormContext } from "react-hook-form";
import { SelectFormField } from "@/components/custom/form-field/select";
import { MultiSelect } from "@/components/ui/multi-select";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";

export type Step2FieldProps = {
  field: any;
  index: number;
};

export function Step2Field(props: Step2FieldProps) {
  const { field, index } = props;
  const { register, control } = useFormContext<TCreateProjectFormData>();

  if (!isValidProjectConfigField(field)) {
    console.warn("Invalid project config field", field);
    return null;
  }

  if (isProjectConfigStringField(field)) {
    return (
      <FormItem>
        <FormLabel>{field.label}</FormLabel>
        <Input
          placeholder={field.placeholder}
          defaultValue={field.defaultValue}
          {...register(`init_config.${index}.value`)}
        />
      </FormItem>
    );
  }

  if (isProjectConfigNumberField(field)) {
    return (
      <FormItem>
        <FormLabel>{field.label}</FormLabel>
        <Input
          type="number"
          min={field.min}
          max={field.max}
          step={field.step}
          defaultValue={field.defaultValue}
          {...register(`init_config.${index}.value`)}
        />
      </FormItem>
    );
  }

  if (isProjectConfigBooleanField(field)) {
    return (
      <Controller
        name={`init_config.${index}.value`}
        control={control}
        render={({ field: _field }) => (
          <FormItem>
            <div
              className="flex items-center gap-3"
              data-value={JSON.stringify(_field)}
            >
              <Checkbox
                id={field.id}
                checked={Boolean(_field.value)}
                onCheckedChange={_field.onChange}
              />
              <FormLabel htmlFor={field.id}>{field.label}</FormLabel>
            </div>
          </FormItem>
        )}
      />
    );
  }

  if (isProjectConfigArrayField(field)) {
    return (
      <Controller
        name={`init_config.${index}.value`}
        control={control}
        defaultValue={field.defaultValue || []}
        render={({ field: _field }) => (
          <FormItem>
            <FormLabel>{field.label}</FormLabel>
            <InputTags {..._field} />
            <input
              readOnly
              className="hidden"
              value={_field.value.join(",")}
              name={field.id}
            />
          </FormItem>
        )}
      />
    );
  }

  if (isProjectConfigSelectField(field)) {
    const options = field.options.map((option) => ({
      label: option.label,
      value: option.id,
    }));

    const placeholder = field.placeholder || `Select ${field.label}`;

    if (field.multiple) {
      return (
        <Controller
          name={`init_config.${index}.value`}
          control={control}
          defaultValue={field.defaultValue || []}
          render={({ field: _field }) => (
            <FormItem>
              <FormLabel>{field.label}</FormLabel>
              <MultiSelect
                options={options}
                onValueChange={_field.onChange}
                defaultValue={_field.value}
                placeholder={placeholder}
                maxCount={field.maxCount}
                variant="secondary"
              />
            </FormItem>
          )}
        />
      );
    }

    return (
      <SelectFormField
        control={control}
        name={`init_config.${index}.value`}
        label={field.label}
        selectProps={{
          disabled: false,
          error: false,
          placeholder,
          noDataMsg: "No data available",
          errorMsg: "Something went wrong!",
          data: options,
        }}
      />
    );
  }

  if (isProjectConfigRadioField(field)) {
    return (
      <Controller
        name={`init_config.${index}.value`}
        control={control}
        defaultValue={field.defaultValue || []}
        render={({ field: _field }) => (
          <FormItem>
            <FormLabel>{field.label}</FormLabel>
            <RadioGroup
              onValueChange={_field.onChange}
              defaultValue={_field.value}
              className="flex flex-col gap-2"
            >
              {field.options.map((option) => (
                <div key={option.id} className="flex items-center gap-3">
                  <RadioGroupItem id={option.id} value={option.id} />
                  <FormLabel htmlFor={option.id}>{option.label}</FormLabel>
                </div>
              ))}
            </RadioGroup>
          </FormItem>
        )}
      />
    );
  }

  console.warn("Unknown field type", field);
  return null;
}
