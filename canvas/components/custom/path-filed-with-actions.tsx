import { TPathRecord } from "@/app/dashboard/project/id/[id]/view/hooks/useParsePathRecordToArray";
import { Input } from "../ui/input";
import React from "react";
import clsx from "clsx";
import { WithTooltip } from "./with-tooltip";

export type TPathFiledWithActionsProps = {
  pathRecord: TPathRecord;
  /**
   * If true then use span to show the path value,
   * else use input component.
   */
  isReadonly?: boolean;
  /**
   * Props passed to input element
   */
  inputProps?: React.HTMLProps<HTMLInputElement>;
  /**
   * Props passed to span element.
   */
  spanProp?: React.HTMLProps<HTMLSpanElement>;

  actions?: { id: string; children: React.ReactNode }[];
};

export function PathFieldWithAction(props: TPathFiledWithActionsProps) {
  const {
    pathRecord,
    inputProps = {},
    spanProp = {},
    isReadonly,
    actions = [],
  } = props;
  const { name, value } = pathRecord;

  const { className: inputClassName, ...inputRest } = inputProps;
  const { className: spanClassName, ...spanRest } = spanProp;

  return (
    <div className="flex items-center text-sm border border-gray-200 rounded-md space-x-1">
      <div className="px-1.5 py-2 bg-accent text-accent-foreground rounded-md">
        {name}
      </div>

      {isReadonly ? (
        <WithTooltip message={value}>
          <span
            className={clsx(
              "flex-1 overflow-hidden whitespace-nowrap text-ellipsis text-gray-400",
              spanClassName
            )}
            {...spanRest}
          >
            {value}
          </span>
        </WithTooltip>
      ) : (
        <Input
          className={clsx(
            "border-none shadow-transparent flex-1",
            inputClassName
          )}
          value={value}
          {...inputRest}
        />
      )}

      {actions.map((action, idx) => (
        <React.Fragment key={action.id}>
          {action.children}
          {idx !== actions.length - 1 && (
            <div className="w-[1px] h-5 border-r border-r-gray-200" />
          )}
        </React.Fragment>
      ))}
    </div>
  );
}
