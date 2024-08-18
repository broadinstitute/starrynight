import { api, TResponse } from "./api";

export type TProjectStep = {
  id: number | string;
  project_id: number | string;
  name: string;
  description: string;
  type: string;
};

export type TGetStepsOptions = {
  canThrowOnError?: boolean;
  projectId: string | number;
};

export async function getSteps(
  options: TGetStepsOptions
): Promise<TResponse<TProjectStep[]>> {
  const { projectId, canThrowOnError } = options;
  try {
    const response = (await api
      .get(`/step/?project_id=${projectId}`)
      .json()) as TProjectStep[];

    return {
      ok: true,
      response,
    };
  } catch (error) {
    console.error(error);

    if (canThrowOnError) {
      throw new Error("Error while fetching steps");
    }

    return {
      error,
    };
  }
}
