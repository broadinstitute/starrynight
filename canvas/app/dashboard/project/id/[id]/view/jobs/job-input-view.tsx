import React from "react";
import { ViewJobInput } from "./view-input";
import { ActionButton } from "@/components/custom/action-button";
import { Pencil } from "lucide-react";

export type TProjectJobInputProps = {
  inputPath: string;
  inputName: string;
  onRequestEditing: () => void;
};

export function ProjectJobInputView(props: TProjectJobInputProps) {
  const { inputPath, inputName, onRequestEditing } = props;

  return (
    <>
      <div className="px-1.5 py-2 bg-accent text-accent-foreground rounded-md">
        {inputName}
      </div>
      <span
        onDoubleClick={onRequestEditing}
        className="flex-1 overflow-hidden whitespace-nowrap text-ellipsis text-gray-400"
      >
        {inputPath}
      </span>
      <ViewJobInput />
      <div className="w-[1px] h-5 border-r border-r-gray-200" />
      <ActionButton
        icon={<Pencil />}
        message="Edit input file"
        onClick={onRequestEditing}
        key="edit-input"
      />
    </>
  );
}
