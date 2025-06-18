import * as React from "react";
import { useModelState, createRender } from "@anywidget/react";
import { Field } from "./field";
import "./globals.css";
import {
  experimentToInputField,
  formToExperimentData,
  isFieldset,
} from "./utils";
import { Button } from "./components/ui/button";

export function App() {
  const [spec, setSpec] = useModelState("spec");
  const [shouldShowSuccessMessage, setShouldShowSuccessMessage] =
    React.useState(false);
  const inputForm = React.useRef<HTMLFormElement>(null);
  const outputForm = React.useRef<HTMLFormElement>(null);

  const inputFields = React.useMemo(() => {
    return experimentToInputField((spec as any).inputs);
  }, []);

  const outputFields = React.useMemo(() => {
    return experimentToInputField((spec as any).outputs as any);
  }, []);

  const handleSubmit = React.useCallback(() => {
    if (!inputForm.current || !outputForm.current) {
      console.error("Not able to grab the form.");
      return;
    }

    const inputData = formToExperimentData(inputForm.current, inputFields);
    const outputData = formToExperimentData(outputForm.current, outputFields);

    setSpec({
      ...(spec as any),
      inputs: inputData,
      outputs: outputData,
    });
    setShouldShowSuccessMessage(true);
  }, [inputFields, outputFields]);

  if (shouldShowSuccessMessage) {
    return (
      <div
        className="flex items-center p-4 mb-4 text-sm text-green-800 rounded-lg bg-green-100"
        role="alert"
      >
        <svg
          className="w-5 h-5 mr-2 text-green-700"
          fill="currentColor"
          viewBox="0 0 20 20"
        >
          <path
            fillRule="evenodd"
            d="M16.707 5.293a1 1 0 010 1.414L8.414 15l-4.121-4.121a1 1 0 011.414-1.414L8.414 12.172l7.293-7.293a1 1 0 011.414 0z"
            clipRule="evenodd"
          />
        </svg>
        <span className="font-medium mr-0.5">Success!</span> Spec has been
        updated.
      </div>
    );
  }

  return (
    <div className="p-4">
      <form ref={inputForm} className="flex flex-col gap-6 w-full">
        <h1 className="font-bold text-2xl">Inputs Specs</h1>
        {inputFields.map((field) => {
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
      </form>
      <form ref={outputForm} className="flex flex-col gap-6 w-full">
        <h1 className="font-bold text-2xl">Output Specs</h1>
        {outputFields.map((field) => {
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
      </form>
      <div className="flex justify-end">
        <Button onClick={handleSubmit}>Save Changes</Button>
      </div>
    </div>
  );
}

export default {
  render: createRender(App),
};
