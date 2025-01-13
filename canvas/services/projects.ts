import { useMutation, useQuery } from "@tanstack/react-query";
import { api } from "./api";

// TODO: Updates once BE support sending project status as enum.
export type TProjectStatus =
  | "not-configured"
  | "configuring"
  | "configured"
  | "running"
  | "failed"
  | "success";

export type TProject = {
  id: number | string;
  name: string;
  dataset_uri: string;
  img_uri: string | null;
  description: string;
  type: string;
  parser: string;
  workspace_uri: string;
  storage_uri: string;
  is_configured: boolean;
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
  dataset_uri: string;
  parser_type: string;
  type: string;
  name: string;
  description: string;
  workspace_uri: string;
  storage_uri: string;
  is_configured: boolean;
  init_config: Record<string, unknown>;
};

export function createProject(
  options: TCreateProjectOptions
): Promise<TProject> {
  return api.post(options, "/project").json();
}

export function getParserAndProjectType(): Promise<[string[], string[]]> {
  const parsers = api.get("/project/parser-type").json() as Promise<string[]>;
  const type = api.get("/project/type/all").json() as Promise<string[]>;

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

export type TConfigureProjectOption = {
  project_id: string;
};

export function configureProject(
  options: TConfigureProjectOption
): Promise<TProject> {
  const { project_id } = options;

  return api.post({}, `/project/configure?project_id=${project_id}`).json();
}

export type TUseConfigureProjectOptions = {
  onSuccess: (data: TProject) => void;
  onError: (error: unknown) => void;
};

export function useConfigureProject(options: TUseConfigureProjectOptions) {
  const { onError, onSuccess } = options;

  return useMutation({
    mutationFn: configureProject,
    onError,
    onSuccess,
  });
}

export type TExecuteProjectOptions = {
  project_id: string;
};

export function executeProject(
  options: TExecuteProjectOptions
): Promise<TProject> {
  const { project_id } = options;

  return api.post({ project_id }, "/project/execute").json();
}

export type TUseExecuteProjectOptions = {
  onSuccess: () => void;
  onError: () => void;
};

export function useExecuteProject(options: TUseExecuteProjectOptions) {
  const { onSuccess, onError } = options;

  return useMutation({
    mutationFn: executeProject,
    onError,
    onSuccess,
  });
}
