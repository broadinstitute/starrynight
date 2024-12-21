import { TUseParseJobInput } from "./useParseJobInput";
import React from "react";
import { Input } from "@/components/ui/input";
import { ActionButton } from "@/components/custom/action-button";
import { Check, XIcon } from "lucide-react";
import { JobInputUploadFile } from "./job-input-upload-file";
import { ProjectJobInputEditWarningModal } from "./job-input-edit-warning-modal";

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
      <div className="px-1.5 py-2 bg-accent text-accent-foreground rounded-md">
        {inputName}
      </div>
      <Input
        className="border-none shadow-transparent flex-1"
        autoFocus
        value={inputPath}
        onChange={(e) => onInputPathChange(e.currentTarget.value)}
      />

      <JobInputUploadFile
        inputFile={inputFile}
        updateInputFile={setInputFile}
      />
      <div className="w-[1px] h-5 border-r border-r-gray-200" />
      <ActionButton
        icon={<XIcon />}
        message="Close editing mode"
        className="text-yellow-600 hover:bg-yellow-50 hover:text-yellow-600"
        onClick={handleOnCloseEditingModeClick}
      />
      <div className="w-[1px] h-5 border-r border-r-gray-200" />
      <ActionButton
        onClick={onRequestView}
        icon={<Check />}
        message="Save changes"
        key="save-changes"
      />
      <ProjectJobInputEditWarningModal
        primaryActionCallback={handleOnWarningModalPrimaryActionClick}
        isOpen={isWarningModalOpen}
        onOpenChange={setIsWarningModalOpen}
      />
    </>
  );
}
