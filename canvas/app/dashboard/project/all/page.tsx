import { Suspense } from "react";
import { PageContainer } from "../../_layout/page-container";
import { AllProjects } from "./all-projects";
import { AllProjectsHeading } from "./all-projects-heading";
import { AllProjectSkeleton } from "./all-projects-skeleton";
import { NoProjects } from "./no-projects";

export default function AllProjectPage() {
  return (
    <PageContainer>
      <AllProjectsHeading />
      <Suspense fallback={<AllProjectSkeleton />}>
        <AllProjects />
      </Suspense>
    </PageContainer>
  );
}
