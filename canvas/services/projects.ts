import { api, TResponse } from "./api";

export type TProject = {
  id: number | string;
  name: string;
  dataset_uri: string;
  img_uri: string | null;
  description: string;
  type: string;
  parser: string;
};

export async function getProjects(): Promise<TResponse<TProject>> {
  try {
    const response = (await api.get("/project").json()) as TProject;
    return {
      ok: true,
      response,
    };
  } catch (error) {
    console.error(error);
    return {
      error,
    };
  }
}

export type TGetProjectOptions = {
  id: string;
};

export async function getProject(
  options: TGetProjectOptions
): Promise<TResponse<TProject>> {
  const { id } = options;

  try {
    const response = (await api.get(`/project/id/${id}`).json()) as TProject;

    return {
      ok: true,
      response,
    };
  } catch (error) {
    console.error(error);
    return {
      error,
    };
  }
}

export type TCreateProjectOptions = {
  dataset: string;
  parser: string;
  type: string;
  name: string;
  description: string;
};

export async function createProject(
  options: TCreateProjectOptions
): Promise<TProject> {
  const { dataset, parser, type, name, description } = options;
  const response = (await api
    .post(
      {
        name,
        description,
        type,
        parser_type: parser,
        dataset_uri: dataset,
      },
      "/project"
    )
    .json()) as TProject;

  return response;
}

export async function getParserAndProjectType(): Promise<
  TResponse<[string[], string[]]>
> {
  try {
    const parsers = api.get("/project/parser-type").json();
    const type = api.get("/project/type").json();

    const response = (await Promise.all([parsers, type])) as [
      string[],
      string[]
    ];

    return {
      ok: true,
      response,
    };
  } catch (error) {
    console.log("Error", error);
    return {
      error,
    };
  }
}
