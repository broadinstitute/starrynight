import {
  TProjectExperiment,
  TProjectExperimentObjInput,
  TProjectExperimentValidInput,
} from "@/services/projects";
import { snakeCaseTitleCase } from "@/utils/misc";

export type TExperimentToInputFieldInputType = "string" | "array" | "boolean";

export type TExperimentToInputFieldCommon = {
  path: string;
  name: string;
  type: "input" | "fieldset";
};

export type TExperimentToInputStringField = TExperimentToInputFieldCommon & {
  inputType: TExperimentToInputFieldInputType;
  value: string | boolean;
};

export type TExperimentToInputFieldset = TExperimentToInputFieldCommon & {
  children: TExperimentToInputStringField[];
};

export type TExperimentToInputField =
  | TExperimentToInputStringField
  | TExperimentToInputFieldset;

function getInputFieldType(
  value: string | string[] | boolean | null | undefined,
): TExperimentToInputFieldInputType {
  if (typeof value === "boolean") return "boolean";
  return Array.isArray(value) ? "array" : "string";
}

function experimentKeyValueToInputField(
  key: string,
  value: string | string[] | boolean | null | undefined,
): TExperimentToInputStringField {
  const inputType = getInputFieldType(value);
  let _v = value;

  if (typeof value === "boolean") {
    _v = value;
  } else if (!value) {
    _v = "";
  }

  return {
    inputType,
    value: _v as string | boolean,
    name: snakeCaseTitleCase(key),
    path: key,
    type: "input",
  };
}

function experimentObjectValueToInputField(
  key: string,
  value: TProjectExperimentObjInput,
): TExperimentToInputFieldset {
  const children = [] as TExperimentToInputStringField[];
  for (const [k, v] of Object.entries(value)) {
    children.push(experimentKeyValueToInputField(k, v));
  }

  return {
    children,
    path: key,
    name: snakeCaseTitleCase(key),
    type: "fieldset",
  };
}

export function experimentToInputField(
  experiemnt: TProjectExperiment,
): TExperimentToInputField[] {
  const fields = [] as TExperimentToInputField[];

  for (const [key, value] of Object.entries(experiemnt)) {
    if (key === "init_config_" || key === "init_config") {
      // We don't want to process init_config.
      continue;
    }

    if (
      typeof value === "string" ||
      Array.isArray(value) ||
      typeof value === "boolean" ||
      !value
    ) {
      fields.push(experimentKeyValueToInputField(key, value));
    } else {
      fields.push(experimentObjectValueToInputField(key, value));
    }
  }

  return fields;
}

export function isFieldset(
  obj: TExperimentToInputField,
): obj is TExperimentToInputFieldset {
  if (obj.type === "fieldset") {
    return true;
  }
  return false;
}

function getExperimentValueFromFromValue(
  form: HTMLFormElement,
  name: string,
  inputType: TExperimentToInputFieldInputType,
): string | string[] | boolean {
  switch (inputType) {
    case "string":
      return form[name].value;
    case "array":
      return form[name].value.split(",");
    case "boolean":
      return form[name].checked;
    default:
      throw new Error("Not supported");
  }
}

export function formToExperimentData(
  form: HTMLFormElement,
  fields: TExperimentToInputField[],
): TProjectExperiment {
  const experiments = {} as TProjectExperiment;

  for (const field of fields) {
    if (isFieldset(field)) {
      const fieldSet = {} as TProjectExperimentObjInput;

      for (const subField of field.children) {
        fieldSet[subField.path] = getExperimentValueFromFromValue(
          form,
          `${field.path}.${subField.path}`,
          subField.inputType,
        );
      }
      experiments[field.path] = fieldSet;
    } else {
      experiments[field.path] = getExperimentValueFromFromValue(
        form,
        field.path,
        field.inputType,
      );
    }
  }

  return experiments;
}
