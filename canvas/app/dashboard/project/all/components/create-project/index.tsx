import React from "react";
import { CreateProjectContent } from "./content";
import {
  dehydrate,
  HydrationBoundary,
  QueryClient,
} from "@tanstack/react-query";
import {
  GET_PARSER_AND_PROJECT_TYPE_QUERY_KEY,
  getParserAndProjectType,
} from "@/services/projects";

export async function CreateProject() {
  const queryClient = new QueryClient();

  await queryClient.prefetchQuery({
    queryKey: [GET_PARSER_AND_PROJECT_TYPE_QUERY_KEY],
    queryFn: getParserAndProjectType,
  });

  return (
    <HydrationBoundary state={dehydrate(queryClient)}>
      <CreateProjectContent />
    </HydrationBoundary>
  );
}
