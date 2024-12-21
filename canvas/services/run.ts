import { useQuery } from "@tanstack/react-query";
import { api, TResponse } from "./api";
import { TJobInput, TJobOutput } from "./job";

export type TRunStatus = "pending" | "running" | "success" | "failed" | "init";

export type TRun = {
  id: string | number;
  job_id: string | number;
  name: string;
  run_status: TRunStatus;
  outputs: Record<string, TJobOutput>;
  inputs: Record<string, TJobInput>;
};

export type TGetRunsOptions = {
  job_id: string | number;
};

export async function getRuns(
  options: TGetRunsOptions
): Promise<TResponse<TRun[]>> {
  const { job_id } = options;
  try {
    const response = (await api.get(`/run/?job_id=${job_id}`).json()) as TRun[];

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

export const GET_RUNS_QUERY_KEY = "GET_RUNS_QUERY_KEY";

export type TUseGetRunsOptions = {
  jobId: string | number;
};

export function useGetRuns(options: TUseGetRunsOptions) {
  const { jobId } = options;

  return useQuery({
    queryKey: [GET_RUNS_QUERY_KEY, jobId],
    queryFn: () => getRuns({ job_id: jobId }),
  });
}

export type TCreateRunOptions = {
  id: string | number;
  jobId: string | number;
  name: string;
};

export async function createRun(
  options: TCreateRunOptions
): Promise<TResponse<TRun>> {
  const { jobId, name, id } = options;
  try {
    const response = (await api
      .post(
        {
          name,
          id,
          job_id: jobId,
        },
        "/run"
      )
      .json()) as TRun;

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
