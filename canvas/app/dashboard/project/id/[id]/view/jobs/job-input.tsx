import { TUseParseJobInput } from "./useParseJobInput";
import React from "react";
import { ProjectJobInputView } from "./job-input-view";
import { ProjectJobInputEdit } from "./job-input-edit";

export type TProjectJobInputProps = {
  input: TUseParseJobInput;
};

export function ProjectJobInput(props: TProjectJobInputProps) {
  const { input } = props;
  const [isEditing, setIsEditing] = React.useState(false);
  const [inputPath, setInputPath] = React.useState(input.value);

  const onRequestEditing = React.useCallback(() => {
    setIsEditing(true);
  }, []);

  const onRequestView = React.useCallback(() => {
    setIsEditing(false);
  }, []);

  return (
    <li
      key={input.id}
      className="flex items-center text-sm border border-gray-200 rounded-md space-x-1"
    >
      {isEditing ? (
        <ProjectJobInputEdit
          inputName={input.name}
          inputPath={inputPath}
          onInputPathChange={setInputPath}
          onRequestView={onRequestView}
        />
      ) : (
        <ProjectJobInputView
          onRequestEditing={onRequestEditing}
          inputName={input.name}
          inputPath={inputPath}
        />
      )}
    </li>
  );
}
