import { useQuery } from "@tanstack/react-query";
import { api } from "./api";

export type TProject = {
  id: number | string;
  name: string;
  dataset_uri: string;
  img_uri: string | null;
  description: string;
  type: string;
  parser: string;
  workspace_uri: string;
};

export function getProjects(): Promise<TProject[]> {
  return api.get("/project").json();
}

export const GET_PROJECTS_QUERY_KEY = "GET_PROJECTS_QUERY_KEY";

export function useGetProjects() {
  return useQuery({
    queryKey: [GET_PROJECTS_QUERY_KEY],
    queryFn: getProjects,
  });
}

export type TGetProjectOptions = {
  id: string;
};

export function getProject(options: TGetProjectOptions): Promise<TProject> {
  const { id } = options;

  return api.get(`/project/id/${id}`).json();
}

export const GET_PROJECT_QUERY_KEY = "GET_PROJECT_QUERY_KEY";

export type TUseGetProject = {
  /**
   * Project id
   */
  id: string;
};

export function useGetProject(options: TUseGetProject) {
  const { id } = options;
  return useQuery({
    queryKey: [GET_PROJECT_QUERY_KEY, id],
    queryFn: () => getProject({ id }),
  });
}

export type TCreateProjectOptions = {
  dataset: string;
  parser: string;
  type: string;
  name: string;
  description: string;
  workspaceURI: string;
};

export function createProject(
  options: TCreateProjectOptions
): Promise<TProject> {
  const { dataset, parser, type, name, description, workspaceURI } = options;
  return api
    .post(
      {
        name,
        description,
        type,
        parser_type: parser,
        dataset_uri: dataset,
        workspace_uri: workspaceURI,
      },
      "/project"
    )
    .json();
}

export function getParserAndProjectType(): Promise<[string[], string[]]> {
  const parsers = api.get("/project/parser-type").json() as Promise<string[]>;
  const type = api.get("/project/type").json() as Promise<string[]>;

  return Promise.all([parsers, type]);
}

export const GET_PARSER_AND_PROJECT_TYPE_QUERY_KEY =
  "GET_PARSER_AND_PROJECT_TYPE_QUERY_KEY";

export type TUseGetParserAndProjectTypeOptions = {
  enabled?: boolean;
};

export function useGetParserAndProjectType(
  options: TUseGetParserAndProjectTypeOptions
) {
  return useQuery({
    queryKey: [GET_PARSER_AND_PROJECT_TYPE_QUERY_KEY],
    queryFn: getParserAndProjectType,
    ...options,
  });
}
