import { Loader2 } from "lucide-react";
import React from "react";
import {
  ButtonWithTooltip,
  TButtonWithTooltipProps,
} from "./button-with-tooltip";
import clsx from "clsx";

export type TActionsButtonProps = TButtonWithTooltipProps & {
  isLoading?: boolean;
  icon?: React.ReactNode;
  childSpan?: React.HTMLProps<HTMLSpanElement>;
};

export const ActionButton = React.forwardRef<
  HTMLButtonElement,
  TActionsButtonProps
>(function _ActionButton(props, ref) {
  const { isLoading, icon, className, children, childSpan, ...rest } = props;

  const [_icon, setIcon] = React.useState(icon);

  React.useEffect(() => {
    if (isLoading) {
      setIcon(<Loader2 />);
    } else {
      setIcon(icon);
    }
  }, [icon, isLoading]);

  return (
    <ButtonWithTooltip
      disabled={isLoading}
      size="icon"
      variant="ghost"
      className={className}
      ref={ref}
      {...rest}
    >
      <span className={clsx(isLoading && "animate-spin")}>{_icon}</span>
      <span
        {...childSpan}
        className={clsx("md:hidden lg:inline", childSpan?.className)}
      >
        {children}
      </span>
    </ButtonWithTooltip>
  );
});
