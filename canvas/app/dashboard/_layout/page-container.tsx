import clsx from "clsx";
import React from "react";

export type TPageContainer = React.HTMLProps<HTMLDivElement>;

export function PageContainer(props: TPageContainer) {
  const { children, className } = props;

  return (
    <div
      className={clsx(
        "px-0 py-4 md:px-4 flex flex-col flex-1 relative",
        className
      )}
    >
      {children}
    </div>
  );
}
