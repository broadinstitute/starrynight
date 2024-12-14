import { GET_PROJECT_QUERY_KEY, getProjects } from "@/services/projects";
import { AllProjectsView } from "./view";
import {
  dehydrate,
  HydrationBoundary,
  QueryClient,
} from "@tanstack/react-query";

export async function AllProjectsModel() {
  const queryClient = new QueryClient();

  await queryClient.prefetchQuery({
    queryKey: [GET_PROJECT_QUERY_KEY],
    queryFn: getProjects,
  });

  return (
    <HydrationBoundary state={dehydrate(queryClient)}>
      <AllProjectsView />
    </HydrationBoundary>
  );
}
