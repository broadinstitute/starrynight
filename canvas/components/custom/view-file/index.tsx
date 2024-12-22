import React from "react";
import { ActionButton, TActionsButtonProps } from "../action-button";
import { Eye } from "lucide-react";

export type TViewFileProps = {
  trigger?: React.ReactNode;
  defaultTriggerProps?: TActionsButtonProps;
};

export function ViewFile(props: TViewFileProps) {
  const { trigger, defaultTriggerProps = { message: "View file" } } = props;

  return (
    <>{trigger || <ActionButton icon={<Eye />} {...defaultTriggerProps} />}</>
  );
}
