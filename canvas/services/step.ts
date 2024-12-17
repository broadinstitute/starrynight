import { useQuery } from "@tanstack/react-query";
import { api, TResponse } from "./api";

export type TStep = {
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
): Promise<TResponse<TStep[]>> {
  const { projectId, canThrowOnError } = options;
  try {
    const response = (await api
      .get(`/step/?project_id=${projectId}`)
      .json()) as TStep[];

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

export const GET_STEPS_QUERY_KEY = "GET_STEPS_QUERY_KEY";

export type TUseGetStepsOptions = {
  /**
   * Project id
   */
  id: string | number;
};

export function useGetSteps(options: TUseGetStepsOptions) {
  const { id } = options;
  return useQuery({
    queryKey: [GET_STEPS_QUERY_KEY, id],
    queryFn: () => getSteps({ projectId: id }),
  });
}
