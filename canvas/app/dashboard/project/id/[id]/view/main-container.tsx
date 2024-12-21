import clsx from "clsx";
import React from "react";

export type TProjectMainContainerProps = React.HTMLProps<HTMLDivElement>;

export function ProjectMainContainer(props: TProjectMainContainerProps) {
  const { className, ...rest } = props;

  return (
    <div
      className={clsx(
        "grid flex-1 grid-cols-1 md:grid-cols-12 gap-6",
        className
      )}
      {...rest}
    />
  );
}
