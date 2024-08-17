"use client";

import { PlusIcon } from "lucide-react";
import { PageHeading } from "../../_components/page-heading";

export function AllProjectsHeading() {
  return (
    <PageHeading
      heading="All Projects"
      primaryAction={{
        onClick: () => console.log("Adding a new project"),
        children: "Create Project",
      }}
    />
  );
}
