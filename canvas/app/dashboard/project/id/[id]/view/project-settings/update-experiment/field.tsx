import React from "react";
import { TExperimentToInputStringField } from "./utils";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";
import { InputTags } from "@/components/ui/input-tags";
import { Input } from "@/components/ui/input";

export function Field(props: { field: TExperimentToInputStringField }) {
  const { field } = props;
  const [isTouched, setIsTouched] = React.useState(false);

  const [value, setValues] = React.useState(
    (Array.isArray(field.value) ? field.value : []) as string[],
  );

  if (typeof field.value === "boolean") {
    return (
      <div className="flex items-center gap-3">
        <Checkbox
          onChange={() => setIsTouched(true)}
          name={field.path}
          defaultChecked={field.value}
          className={isTouched ? "border-primary" : ""}
        />
        <Label htmlFor={field.path}>{field.name}</Label>
      </div>
    );
  }

  if (field.inputType === "array") {
    return (
      <div className="flex flex-col gap-3">
        <Label htmlFor={field.path}>{field.name}</Label>
        <InputTags
          className={isTouched ? "border-primary" : ""}
          value={value}
          onChange={(val) => {
            setValues(val);
            setIsTouched(true);
          }}
        />
        <input
          readOnly
          className="hidden"
          value={value.join(",")}
          name={field.path}
        />
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-3">
      <Label htmlFor={field.path}>{field.name}</Label>
      <Input
        className={isTouched ? "border-primary" : ""}
        onChange={() => setIsTouched(true)}
        name={field.path}
        defaultValue={field.value}
      />
    </div>
  );
}
