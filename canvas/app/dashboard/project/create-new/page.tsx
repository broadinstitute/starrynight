import React from "react";
import {
  dehydrate,
  HydrationBoundary,
  QueryClient,
} from "@tanstack/react-query";
import {
  GET_PARSER_AND_PROJECT_TYPE_QUERY_KEY,
  getParserAndProjectType,
} from "@/services/projects";
import { PageContainer } from "../../_layout/page-container";
import { CreateNewProjectHeading } from "./heading";
import { CreateNewProjectForm } from "./form";

export default async function CreateNewProjectPage() {
  const queryClient = new QueryClient();

  await queryClient.prefetchQuery({
    queryKey: [GET_PARSER_AND_PROJECT_TYPE_QUERY_KEY],
    queryFn: getParserAndProjectType,
  });

  return (
    <HydrationBoundary state={dehydrate(queryClient)}>
      <PageContainer>
        <CreateNewProjectHeading />
        <CreateNewProjectForm />
      </PageContainer>
    </HydrationBoundary>
  );
}
