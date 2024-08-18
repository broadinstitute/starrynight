import { Suspense } from "react";
import { PageContainer } from "../../_layout/page-container";
import { ProjectMainContent } from "./main-content";
import { ProjectSkeleton } from "./skeleton";
import { getProject } from "@/services/projects";

type TProjectPageProps = {
  params: {
    id: string;
  };
};

export default async function ProjectPage(props: TProjectPageProps) {
  const { params } = props;

  return (
    <PageContainer>
      <Suspense fallback={<ProjectSkeleton />}>
        <ProjectMainContent />
      </Suspense>
    </PageContainer>
  );
}
