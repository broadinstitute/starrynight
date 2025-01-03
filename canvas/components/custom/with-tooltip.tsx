import React from "react";
import { Tooltip, TooltipContent, TooltipTrigger } from "../ui/tooltip";

export type TWithTooltipProps = React.PropsWithChildren<{
  message: string;
}>;

export function WithTooltip(props: TWithTooltipProps) {
  const { message, children } = props;
  return (
    <Tooltip>
      <TooltipTrigger asChild>{children}</TooltipTrigger>
      <TooltipContent className="max-w-48">{message}</TooltipContent>
    </Tooltip>
  );
}
