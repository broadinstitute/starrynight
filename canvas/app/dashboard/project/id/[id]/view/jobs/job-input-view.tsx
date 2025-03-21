import React, { useMemo } from "react";
import { ActionButton } from "@/components/custom/action-button";
import { Pencil } from "lucide-react";
import {
  PathFieldWithAction,
  TPathFiledWithActionsProps,
} from "@/components/custom/path-filed-with-actions";
import { ViewFile } from "@/components/custom/view-file";

export type TProjectJobInputProps = {
  inputPath: string;
  inputName: string;
  onRequestEditing: () => void;
};

export function ProjectJobInputView(props: TProjectJobInputProps) {
  const { inputPath, inputName, onRequestEditing } = props;

  const actions = useMemo(() => {
    const _actions: TPathFiledWithActionsProps["actions"] = [];

    if (inputPath) {
      _actions.push({
        id: "view-job-input",
        children: (
          <ViewFile
            url={inputPath}
            key="view-job-input"
            defaultTriggerProps={{ message: "View input file." }}
          />
        ),
      });
    }

    _actions.push({
      id: "edit-job-input",
      children: (
        <ActionButton
          icon={<Pencil />}
          message="Edit input file"
          onClick={onRequestEditing}
          key="edit-input"
        />
      ),
    });

    return _actions;
  }, [inputPath, onRequestEditing]);

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
      actions={actions}
    />
  );
}
