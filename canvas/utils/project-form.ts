export type TProjectConfigBaseFieldType =
  | "string"
  | "number"
  | "boolean"
  | "radio"
  | "array"
  | "select";

export type TProjectConfigBaseField = {
  id: string;
  label: string;
  isRequired: boolean;
  fieldType: TProjectConfigBaseFieldType;
  description?: string;
};

export type TProjectConfigStringField = TProjectConfigBaseField & {
  fieldType: "string";
  defaultValue?: string;
  placeholder?: string;
  maxLength?: number;
};

export type TProjectConfigNumberField = TProjectConfigBaseField & {
  fieldType: "number";
  defaultValue?: number;
  min?: number;
  max?: number;
  step?: number;
};

export type TProjectConfigBooleanField = TProjectConfigBaseField & {
  fieldType: "boolean";
  defaultValue?: boolean;
};

export type TProjectConfigSelectOptionsLikeOptions = {
  label: string;
  id: string;
};

export type TProjectConfigRadioField = TProjectConfigBaseField & {
  fieldType: "radio";
  defaultValue?: string;
  options: Array<TProjectConfigSelectOptionsLikeOptions>;
};

export type TProjectConfigSelectField = TProjectConfigBaseField & {
  fieldType: "select";
  options: Array<TProjectConfigSelectOptionsLikeOptions>;
  multiple?: boolean;
  maxCount?: number;
  defaultValue?: string;
  placeholder?: string;
};

export type TProjectConfigArrayField = TProjectConfigBaseField & {
  fieldType: "array";
  inputType: "string" | "number" | "mixed";
  maxLength?: number;
  defaultValue?: Array<string>;
};

export type TProjectInitConfig = Array<
  | TProjectConfigStringField
  | TProjectConfigNumberField
  | TProjectConfigBooleanField
  | TProjectConfigSelectField
  | TProjectConfigRadioField
  | TProjectConfigArrayField
>;

export function isValidProjectConfigField(
  field: unknown,
): field is TProjectConfigBaseField {
  if (
    typeof field !== "object" ||
    field === null ||
    !("fieldType" in field) ||
    typeof field.fieldType !== "string"
  )
    return false;

  return (
    field.fieldType === "string" ||
    field.fieldType === "number" ||
    field.fieldType === "boolean" ||
    field.fieldType === "select" ||
    field.fieldType === "radio" ||
    field.fieldType === "array"
  );
}

export function isProjectConfigStringField(
  field: unknown,
): field is TProjectConfigStringField {
  if (!isValidProjectConfigField(field)) return false;

  return field.fieldType === "string";
}

export function isProjectConfigNumberField(
  field: unknown,
): field is TProjectConfigNumberField {
  if (!isValidProjectConfigField(field)) return false;

  return field.fieldType === "number";
}

export function isProjectConfigArrayField(
  field: unknown,
): field is TProjectConfigArrayField {
  if (!isValidProjectConfigField(field)) return false;

  return field.fieldType === "array";
}

export function isProjectConfigSelectField(
  field: unknown,
): field is TProjectConfigSelectField {
  if (!isValidProjectConfigField(field)) return false;

  return field.fieldType === "select";
}

export function isProjectConfigRadioField(
  field: unknown,
): field is TProjectConfigRadioField {
  if (!isValidProjectConfigField(field)) return false;

  return field.fieldType === "radio";
}

export function isProjectConfigBooleanField(
  field: unknown,
): field is TProjectConfigBooleanField {
  if (
    typeof field !== "object" ||
    field === null ||
    !("fieldType" in field) ||
    typeof field.fieldType !== "string"
  )
    return false;

  return field.fieldType === "boolean";
}

// ------>>>>>>>>>> Util to fake the data for the time being.
const makeId = (prefix: string, index: number) => `${prefix}_${index}`;
const makeOptions = (
  prefix: string,
  count = 3,
): TProjectConfigSelectOptionsLikeOptions[] =>
  Array.from({ length: count }, (_, i) => ({
    label: `${prefix} Option ${i + 1}`,
    id: `${prefix.toLowerCase()}_opt_${i + 1}`,
  }));

const makeBaseField = (
  index: number,
  label: string,
  fieldType: TProjectConfigBaseFieldType,
  isRequired = true,
  description?: string,
): TProjectConfigBaseField => ({
  id: makeId("field", index),
  label,
  fieldType,
  isRequired,
  description,
});

// ----- Generator -----

export const generateMockProjectConfig = (): TProjectInitConfig => {
  const fields: TProjectInitConfig = [];

  // Example field names for variety
  const fieldLabels = [
    "Sample Path",
    "Enable Logging",
    "Image Overlap %",
    "Frame Type",
    "Acquisition Mode",
    "Custom Channel Map",
    "Processing Threads",
    "Software Version",
    "Use Legacy Mode",
    "Primary Channel",
    "Secondary Channel",
    "Mitochondria Channel",
    "Segmentation Map",
    "Experiment Type",
    "Plate Identifier",
    "Batch Number",
    "Quality Score",
    "Normalization Method",
    "Include Outliers",
    "Control Group",
  ];

  fieldLabels.forEach((label, index) => {
    const type = [
      "string",
      "number",
      "boolean",
      "select",
      "select-multiple",
      "radio",
      "array",
    ][index % 6] as TProjectConfigBaseFieldType | "select-multiple";

    const base = makeBaseField(index, label, type as any);

    switch (type) {
      case "string":
        fields.push({
          ...base,
          fieldType: "string",
          placeholder: `Enter ${label.toLowerCase()}`,
          maxLength: 100,
        });
        break;

      case "number":
        fields.push({
          ...base,
          fieldType: "number",
          min: 0,
          max: 100,
          step: 1,
        });
        break;

      case "boolean":
        fields.push({
          ...base,
          fieldType: "boolean",
        });
        break;

      case "select":
        fields.push({
          ...base,
          fieldType: "select",
          options: makeOptions(label),
          placeholder: `Select ${label}`,
          multiple: false,
        });
        break;

      case "select-multiple":
        fields.push({
          ...base,
          fieldType: "select",
          options: makeOptions(label),
          placeholder: `Select ${label}`,
          multiple: true,
          maxCount: 2,
        });
        break;

      case "radio":
        fields.push({
          ...base,
          fieldType: "radio",
          options: makeOptions(label),
        });
        break;

      case "array":
        fields.push({
          ...base,
          fieldType: "array",
          inputType: "string",
          maxLength: 5,
        });
        break;
    }
  });

  return fields;
};
