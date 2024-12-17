import clsx from "clsx";
import React from "react";

export type TPageHeadingProps = {
  /**
   * If defined then heading will be shown.
   */
  heading?: React.ReactNode;
  children?: React.ReactNode;
  className?: string;
};

export function PageHeading(props: TPageHeadingProps) {
  const { heading, children, className } = props;

  return (
    <div
      className={clsx(
        "flex mt-3 flex-col pb-4 border-b mb-4 md:flex-row md:justify-between md:items-center md:mt-6 md:border-b-slate-200",
        className
      )}
    >
      <div>
        <div className="font-thin text-4xl md:text-5xl">{heading}</div>
      </div>
      {children}
    </div>
  );
}
