import { useMutation, useQuery } from "@tanstack/react-query";
import { api } from "./api";
import { TSpecPathRecord } from "./misc";

export type TRunStatus = "pending" | "running" | "success" | "failed" | "init";

export type TRun = {
  id: string | number;
  job_id: string | number;
  name: string;
  run_status: TRunStatus;
  spec: {
    outputs: Record<string, TSpecPathRecord>;
    inputs: Record<string, TSpecPathRecord>;
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

export type TKillRunOptions = {
  run_id: string | number;
};

export function killRun(options: TKillRunOptions) {
  const { run_id } = options;

  const searchParams = new URLSearchParams();
  searchParams.set("run_id", run_id.toString());

  return api.post({}, `/run/kill?${searchParams.toString()}`).json();
}

export type TUseKillRunOptions = {
  onError: () => void;
  onSuccess: () => void;
};

export function useKillRun(options: TUseKillRunOptions) {
  const { onError, onSuccess } = options;

  return useMutation({
    mutationFn: killRun,
    onError,
    onSuccess,
  });
}
