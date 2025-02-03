import { PageHeading } from "@/components/custom/page-heading";
import { ProjectActions } from "./actions";
import { useProjectStore } from "@/stores/project";
import React from "react";
import { PROJECTS_LISTING_URL } from "@/constants/routes";

export function ProjectHeading() {
  const { name } = useProjectStore((state) => ({ name: state.project.name }));

  return (
    <PageHeading
      heading={name}
      withBackButton={{
        href: PROJECTS_LISTING_URL,
      }}
      className="md:mb-0"
    >
      <ProjectActions />
    </PageHeading>
  );
}
