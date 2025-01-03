import React from "react";
import { ActionButton } from "@/components/custom/action-button";
import { Pencil } from "lucide-react";
import { PathFieldWithAction } from "@/components/custom/path-filed-with-actions";
import { ViewFile } from "@/components/custom/view-file";

export type TProjectJobInputProps = {
  inputPath: string;
  inputName: string;
  onRequestEditing: () => void;
};

export function ProjectJobInputView(props: TProjectJobInputProps) {
  const { inputPath, inputName, onRequestEditing } = props;

  return (
    <PathFieldWithAction
      pathRecord={{
        id: inputPath,
        name: inputName,
        type: "path",
        value: inputPath,
      }}
      isReadonly
      spanProp={{
        onDoubleClick: onRequestEditing,
      }}
      actions={[
        {
          id: "view-job-input",
          children: (
            <ViewFile
              url={inputPath}
              key="view-job-input"
              defaultTriggerProps={{ message: "View input file." }}
            />
          ),
        },
        {
          id: "edit-job-input",
          children: (
            <ActionButton
              icon={<Pencil />}
              message="Edit input file"
              onClick={onRequestEditing}
              key="edit-input"
            />
          ),
        },
      ]}
    />
  );
}
