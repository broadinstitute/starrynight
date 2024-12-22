import React from "react";
import { ActionButton } from "@/components/custom/action-button";
import { Check, XIcon } from "lucide-react";
import { JobInputUploadFile } from "./job-input-upload-file";
import { ProjectJobInputEditWarningModal } from "./job-input-edit-warning-modal";
import { PathFieldWithAction } from "@/components/custom/path-filed-with-actions";

export type TProjectJobInputProps = {
  inputPath: string;
  inputName: string;
  onInputPathChange: (value: string) => void;
  onRequestView: () => void;
};

export function ProjectJobInputEdit(props: TProjectJobInputProps) {
  const { onRequestView, inputName, inputPath, onInputPathChange } = props;
  const [isWarningModalOpen, setIsWarningModalOpen] = React.useState(false);
  const oldValue = React.useRef(inputPath);

  // To upload new file.
  const [inputFile, setInputFile] = React.useState<File | null>(null);

  const handleOnCloseEditingModeClick = React.useCallback(() => {
    if (inputFile) {
      // If input file is not null, we have some files to upload.
      // Before closing edit mode, we need to show the warning.
      setIsWarningModalOpen(true);
      return;
    }

    if (oldValue.current !== inputPath) {
      // Input has been changed, so we need to show the warning,
      // before closing the edit mode.
      setIsWarningModalOpen(true);
      return;
    }

    onRequestView();
  }, [inputFile, onRequestView, inputPath]);

  const handleOnWarningModalPrimaryActionClick = React.useCallback(() => {
    setInputFile(null);
    onInputPathChange(oldValue.current);
    onRequestView();
  }, [onInputPathChange, onRequestView]);

  return (
    <>
      <PathFieldWithAction
        pathRecord={{
          id: inputPath,
          name: inputName,
          type: "path",
          value: inputPath,
        }}
        inputProps={{
          onChange: (e) => onInputPathChange(e.currentTarget.value),
          autoFocus: true,
        }}
        actions={[
          {
            id: "upload-file",
            children: (
              <JobInputUploadFile
                inputFile={inputFile}
                updateInputFile={setInputFile}
              />
            ),
          },
          {
            id: "close-editing-mode",
            children: (
              <ActionButton
                icon={<XIcon />}
                message="Close editing mode"
                className="text-yellow-600 hover:bg-yellow-50 hover:text-yellow-600"
                onClick={handleOnCloseEditingModeClick}
              />
            ),
          },
          {
            id: "save-changes",
            children: (
              <ActionButton
                onClick={onRequestView}
                icon={<Check />}
                message="Save changes"
                key="save-changes"
              />
            ),
          },
        ]}
      />

      <ProjectJobInputEditWarningModal
        primaryActionCallback={handleOnWarningModalPrimaryActionClick}
        isOpen={isWarningModalOpen}
        onOpenChange={setIsWarningModalOpen}
      />
    </>
  );
}
