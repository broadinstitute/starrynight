import { Suspense } from "react";
import { PageContainer } from "../../_layout/page-container";
import { AllProjectsModel } from "./model";
import { AllProjectsSkeleton } from "./view/skeleton";
import { AllProjectsHeading } from "./components/heading";

export default function AllProjectPage() {
  return (
    <PageContainer>
      <AllProjectsHeading />
      <Suspense fallback={<AllProjectsSkeleton />}>
        <AllProjectsModel />
      </Suspense>
    </PageContainer>
  );
}
