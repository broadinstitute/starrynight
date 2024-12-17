import { PageHeading } from "@/components/custom/page-heading";
import { ProjectActions } from "./actions";
import { useProjectStore } from "@/stores/project";
import { buttonVariants } from "@/components/ui/button";
import { ChevronLeft } from "lucide-react";
import React from "react";
import { PROJECTS_LISTING_URL } from "@/constants/routes";
import Link from "next/link";
import clsx from "clsx";
import { WithTooltip } from "@/components/custom/with-tooltip";

export function ProjectHeading() {
  const { name } = useProjectStore((state) => ({ name: state.project.name }));

  return (
    <PageHeading
      heading={
        <div className="flex items-center">
          <WithTooltip message="Go back">
            <Link
              className={clsx(
                buttonVariants({ variant: "ghost", size: "icon" }),
                "mr-2"
              )}
              href={PROJECTS_LISTING_URL}
            >
              <ChevronLeft />
            </Link>
          </WithTooltip>

          {name}
        </div>
      }
      className="md:mb-0"
    >
      <ProjectActions />
    </PageHeading>
  );
}
