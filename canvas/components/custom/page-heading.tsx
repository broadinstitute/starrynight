import clsx from "clsx";
import React from "react";
import { WithTooltip } from "./with-tooltip";
import Link from "next/link";
import { buttonVariants } from "../ui/button";
import { ChevronLeft } from "lucide-react";

export type TPageHeadingProps = {
  /**
   * If defined then heading will be shown.
   */
  heading: React.ReactNode;
  withBackButton?: {
    href: string;
  };
  children?: React.ReactNode;
  className?: string;
};

export function PageHeading(props: TPageHeadingProps) {
  const { heading, children, className, withBackButton } = props;

  return (
    <div
      className={clsx(
        "flex mt-3 flex-col pb-4 border-b mb-4 md:flex-row md:justify-between md:items-center md:mt-6 md:border-b-slate-200",
        className
      )}
    >
      <div>
        <div className="font-thin text-4xl md:text-5xl">
          <div className="flex items-center">
            {withBackButton && (
              <WithTooltip message="Go back">
                <Link
                  className={clsx(
                    buttonVariants({ variant: "ghost", size: "icon" }),
                    "mr-2"
                  )}
                  href={withBackButton.href}
                >
                  <ChevronLeft />
                </Link>
              </WithTooltip>
            )}
            {heading}
          </div>
        </div>
      </div>
      {children}
    </div>
  );
}
