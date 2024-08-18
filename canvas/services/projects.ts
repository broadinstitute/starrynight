import { api, TResponse } from "./api";

export async function getProjects(): Promise<TResponse> {
  try {
    const response = await api.get("/projects").json();
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
): Promise<TResponse> {
  const { id } = options;
  return new Promise((resolve) => setTimeout(resolve, 3000));

  try {
    const response = await api.get(`/project/${id}`).json();

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
};

export async function createProject(options: TCreateProjectOptions) {
  const { dataset, parser } = options;

  try {
    const response = await api.post({ dataset, parser }, "/project").json();
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
