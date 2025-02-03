"use client";

import { PageHeading } from "@/components/custom/page-heading";
import { PROJECTS_LISTING_URL } from "@/constants/routes";

export function CreateNewProjectHeading() {
  return (
    <PageHeading
      heading="Create New Project"
      withBackButton={{ href: PROJECTS_LISTING_URL }}
    />
  );
}
