import { Loader2 } from "lucide-react";
import React from "react";
import {
  ButtonWithTooltip,
  TButtonWithTooltipProps,
} from "./button-with-tooltip";
import clsx from "clsx";

export type TActionsButtonProps = Omit<TButtonWithTooltipProps, "variant"> & {
  isLoading?: boolean;
  icon?: React.ReactNode;
  childSpan?: React.HTMLProps<HTMLSpanElement>;
  variant?:
    | TButtonWithTooltipProps["variant"]
    | "ghost-destructive"
    | "ghost-warning";
};

export const ActionButton = React.forwardRef<
  HTMLButtonElement,
  TActionsButtonProps
>(function ActionButton_(props, ref) {
  const {
    isLoading,
    icon,
    className,
    children,
    childSpan,
    variant: _variant,
    ...rest
  } = props;

  const [_icon, setIcon] = React.useState(icon);
  const variant =
    _variant && _variant !== "ghost-destructive" && _variant !== "ghost-warning"
      ? _variant
      : "ghost";

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
      variant={variant}
      className={clsx(
        className,
        _variant === "ghost-destructive" &&
          "text-red-500 hover:text-red-500 hover:bg-red-50",
        _variant === "ghost-warning" &&
          "text-yellow-600 hover:bg-yellow-50 hover:text-yellow-600"
      )}
      ref={ref}
      {...rest}
    >
      <span className={clsx(isLoading && "animate-spin")}>{_icon}</span>
      {children && (
        <span
          {...childSpan}
          className={clsx("md:hidden lg:inline", childSpan?.className)}
        >
          {children}
        </span>
      )}
    </ButtonWithTooltip>
  );
});
