import { TProjectStepJobInput } from "@/services/job";
import React from "react";
import { ViewInputModal } from "./view-input-modal";

export type TViewInputProps = {
  inputsRecord: Record<string, TProjectStepJobInput>;
  isEditable?: boolean;
  title: string;
  viewButtonTitle: string;
  emptyInputPlaceholder?: string;
  primaryAction?: {
    label: string;
    onClick: (values: Record<string, TProjectStepJobInput>) => void;
  };
};

export function ViewInput(props: TViewInputProps) {
  const {
    inputsRecord,
    isEditable = false,
    title,
    primaryAction,
    emptyInputPlaceholder,
    viewButtonTitle,
  } = props;
  const inputs = React.useMemo(() => {
    const _inputs = Object.entries(inputsRecord);
    return _inputs.map((input) => ({
      id: input[0],
      label: input[0],
      value: input[1].value,
      type: input[1].type,
    }));
  }, Object.keys(inputsRecord));

  return (
    <ViewInputModal
      emptyInputPlaceholder={emptyInputPlaceholder}
      isEditable={isEditable}
      buttonTitle={viewButtonTitle}
      title={title}
      inputs={inputs}
      primaryAction={primaryAction}
    />
  );
}
