import { useQuery } from "@tanstack/react-query";
import { api } from "./api";

export type TStep = {
  id: number | string;
  project_id: number | string;
  name: string;
  description: string;
  type: string;
};

export type TGetStepsOptions = {
  projectId: string | number;
};

export function getSteps(options: TGetStepsOptions): Promise<TStep[]> {
  const { projectId } = options;
  return api.get(`/step/?project_id=${projectId}`).json();
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
