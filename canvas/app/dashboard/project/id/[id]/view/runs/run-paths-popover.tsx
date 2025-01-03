import {
  Popover,
  PopoverTrigger,
  PopoverContent,
} from "@/components/ui/popover";
import { TPathRecord } from "../hooks/useParsePathRecordToArray";
import React from "react";
import { PathFieldWithAction } from "@/components/custom/path-filed-with-actions";
import { ViewFile } from "@/components/custom/view-file";
import {
  ButtonWithTooltip,
  TButtonWithTooltipProps,
} from "@/components/custom/button-with-tooltip";

export type TRunPathsPopoverProps = {
  paths: TPathRecord[];
  title: string;
  triggerProps: TButtonWithTooltipProps;
  noPathsMessage: string;
  viewActionTooltipMessage: string;
};

export function RunPathsPopover(props: TRunPathsPopoverProps) {
  const {
    paths,
    title,
    noPathsMessage,
    triggerProps,
    viewActionTooltipMessage,
  } = props;

  return (
    <>
      <Popover>
        <PopoverTrigger asChild>
          <ButtonWithTooltip variant="ghost" size="icon" {...triggerProps} />
        </PopoverTrigger>
        <PopoverContent className="text-sm w-96">
          <div className="font-bold mb-2">{title}</div>
          {paths.length === 0 && (
            <p className="text-gray-400">{noPathsMessage}</p>
          )}
          <div className="space-y-2 my-2">
            {paths.map((path) => (
              <PathFieldWithAction
                pathRecord={path}
                isReadonly
                key={path.id}
                actions={[
                  {
                    id: "view-input",
                    children: (
                      <ViewFile
                        url={path.value}
                        defaultTriggerProps={{
                          message: viewActionTooltipMessage,
                        }}
                      />
                    ),
                  },
                ]}
              />
            ))}
          </div>
        </PopoverContent>
      </Popover>
    </>
  );
}
