import { PageContainer } from "../../../_layout/page-container";
import { ProjectMainContent } from "./main-content";
import { getProject } from "@/services/projects";
import { ProjectError } from "./project-error";

type TProjectPageProps = {
  params: {
    id: string;
  };
};

export default async function ProjectPage(props: TProjectPageProps) {
  const { params } = props;
  const data = await getProject({ id: params.id });

  if (!data.ok || !data.response) {
    return <ProjectError />;
  }

  return (
    <PageContainer>
      <ProjectMainContent project={data.response} />
    </PageContainer>
  );
}
