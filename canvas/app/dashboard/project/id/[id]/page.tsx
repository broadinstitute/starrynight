import { PageContainer } from "../../../_layout/page-container";
import { GET_PROJECT_QUERY_KEY, getProject } from "@/services/projects";
import {
  dehydrate,
  HydrationBoundary,
  QueryClient,
} from "@tanstack/react-query";
import { ProjectError } from "./project-error";
import { ProjectModel } from "./model";

type TProjectPageProps = {
  params: {
    id: string;
  };
};

export default async function ProjectPage(props: TProjectPageProps) {
  const {
    params: { id },
  } = props;
  try {
    const queryClient = new QueryClient();

    await queryClient.prefetchQuery({
      queryKey: [GET_PROJECT_QUERY_KEY, id],
      queryFn: () => getProject({ id }),
    });

    return (
      <HydrationBoundary state={dehydrate(queryClient)}>
        <PageContainer>
          <ProjectModel projectId={id} />
        </PageContainer>
      </HydrationBoundary>
    );
  } catch (error) {
    console.error(error);
    return (
      <PageContainer>
        <ProjectError />
      </PageContainer>
    );
  }
}
