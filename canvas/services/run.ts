import { useQuery } from "@tanstack/react-query";
import { api } from "./api";
import { TSpecPathRecord } from "./misc";

export type TRunStatus = "pending" | "running" | "success" | "failed" | "init";

export type TRun = {
  id: string | number;
  job_id: string | number;
  name: string;
  run_status: TRunStatus;
  spec: {
    outputs: TSpecPathRecord[];
    inputs: TSpecPathRecord[];
  };
};

export type TGetRunsOptions = {
  job_id: string | number;
};

export async function getRuns(options: TGetRunsOptions): Promise<TRun[]> {
  const { job_id } = options;
  return api.get(`/run/?job_id=${job_id}`).json();
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
    refetchInterval: 10 * 1000, // 10 seconds
  });
}

export type TCreateRunOptions = {
  id: string | number;
  jobId: string | number;
  name: string;
};

export function createRun(options: TCreateRunOptions): Promise<TRun> {
  const { jobId, name, id } = options;
  return api
    .post(
      {
        name,
        id,
        job_id: jobId,
      },
      "/run"
    )
    .json();
}
