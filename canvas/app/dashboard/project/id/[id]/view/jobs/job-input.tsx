import React from "react";
import { ProjectJobInputView } from "./job-input-view";
import { ProjectJobInputEdit } from "./job-input-edit";
import { TPathRecord } from "../hooks/useParsePathRecordToArray";

export type TProjectJobInputProps = {
  input: TPathRecord;
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
    <>
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
    </>
  );
}
