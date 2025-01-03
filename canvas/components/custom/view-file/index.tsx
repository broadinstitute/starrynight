import React from "react";
import { ActionButton, TActionsButtonProps } from "../action-button";
import { Eye } from "lucide-react";
import { FileViewer } from "../file-viewer";

export type TViewFileProps = {
  trigger?: React.ReactNode;
  defaultTriggerProps?: TActionsButtonProps;
  url?: string;
  file?: File;
};

export function ViewFile(props: TViewFileProps) {
  const {
    trigger,
    defaultTriggerProps = { message: "View file" },
    url,
    file,
  } = props;

  return (
    <FileViewer
      trigger={
        trigger || <ActionButton icon={<Eye />} {...defaultTriggerProps} />
      }
      url={url}
      file={file}
    />
  );
}
