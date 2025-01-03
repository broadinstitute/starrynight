import clsx from "clsx";
import { Loader2 } from "lucide-react";
import React from "react";

export type TPageSpinnerProps = React.HTMLProps<HTMLDivElement>;

export function PageSpinner(props: TPageSpinnerProps) {
  const { className, ...rest } = props;
  return (
    <div
      className={clsx(
        "flex flex-1 justify-center items-center w-full h-full",
        className
      )}
      {...rest}
    >
      <Loader2 className="animate-spin" />
    </div>
  );
}
