import React from "react";
import { TProject } from "@/services/projects";
import {
  experimentToInputField,
  formToExperimentData,
  isFieldset,
} from "./utils";
import { Button } from "@/components/ui/button";
import { PageSpinner } from "@/components/custom/page-spinner";
import { Field } from "./field";
import { useUpdateExperiments } from "./use-update-experiments";

export type TUpdateExperimentViewProps = {
  project: TProject;
  onRequestClose: () => void;
};

export function UpdateExperimentView(props: TUpdateExperimentViewProps) {
  const { project, onRequestClose } = props;
  const form = React.useRef<HTMLFormElement>(null);

  const { isPending, updateExperiments } = useUpdateExperiments({
    onSuccess: onRequestClose,
  });

  const fields = React.useMemo(() => {
    const { experiment } = project;
    if (!experiment) return [];
    return experimentToInputField(experiment);
  }, [project]);

  const handleSubmit = React.useCallback(() => {
    if (!form.current) {
      console.error("Not able to grab the form.");
      return;
    }

    const newExperiments = formToExperimentData(form.current, fields);
    updateExperiments(newExperiments);
  }, [fields, updateExperiments]);

  if (fields.length === 0) {
    return (
      <p className="text-gray-400">
        This project does not have any experiment.
      </p>
    );
  }

  return (
    <form ref={form} className="flex flex-col gap-6 w-full">
      {fields.map((field) => {
        if (isFieldset(field)) {
          return (
            <div key={field.path}>
              <div className="mb-4 font-bold">{field.name}</div>
              <div className="grid gap-4 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
                {field.children.map((subField) => {
                  const path = `${field.path}.${subField.path}`;
                  return <Field field={{ ...subField, path }} key={path} />;
                })}
              </div>
              <hr className="my-8" />
            </div>
          );
        } else {
          return <Field field={field} key={field.path} />;
        }
      })}

      <div className="flex justify-end">
        <Button onClick={handleSubmit} type="button" disabled={isPending}>
          {isPending && <PageSpinner />}
          Save changes
        </Button>
      </div>
    </form>
  );
}
