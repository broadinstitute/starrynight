import { Loader2 } from "lucide-react";
import React from "react";
import {
  ButtonWithTooltip,
  TButtonWithTooltipProps,
} from "./button-with-tooltip";
import clsx from "clsx";

export type TActionsButtonProps = Omit<TButtonWithTooltipProps, "children"> & {
  isLoading?: boolean;
  icon?: React.ReactNode;
};

export const ActionButton = React.forwardRef<
  HTMLButtonElement,
  TActionsButtonProps
>(function _ActionButton(props, ref) {
  const { isLoading, icon, className, ...rest } = props;

  const [child, setChild] = React.useState(icon);

  React.useEffect(() => {
    if (isLoading) {
      setChild(<Loader2 />);
    } else {
      setChild(icon);
    }
  }, [icon, isLoading]);

  return (
    <ButtonWithTooltip
      disabled={isLoading}
      size="icon"
      variant="ghost"
      className={clsx(isLoading && "animate-spin", className)}
      ref={ref}
      {...rest}
    >
      {child}
    </ButtonWithTooltip>
  );
});
