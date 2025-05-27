import { useMutation, useQuery } from "@tanstack/react-query";
import { api } from "./api";
import { TSpecPathRecord } from "./misc";

export type TJobOutput = {
  type: string;
  uri: string;
};

export type TJobInput = {
  type: string;
  value: string;
};

export type TJob = {
  id: string | number;
  step_id: string | number;
  name: string;
  description: string;
  type: string;
  spec: {
    outputs: Record<string, TSpecPathRecord>;
    inputs: Record<string, TSpecPathRecord>;
  };
};

export type TGetJobsOptions = {
  project_id: string | number;
};

export function getJobs(options: TGetJobsOptions): Promise<TJob[]> {
  const { project_id } = options;
  const searchParams = new URLSearchParams();

  searchParams.set("project_id", String(project_id));

  return api.get(`/job/?${searchParams.toString()}`).json();
}

export const GET_JOBS_QUERY_KEY = "GET_JOBS_QUERY_KEY";

export type TUseGetJobsOptions = {
  projectID?: string | number;
};

export function useGetJobs(options: TUseGetJobsOptions) {
  const { projectID } = options;

  return useQuery({
    queryKey: [GET_JOBS_QUERY_KEY, projectID],
    // queryFn will only run if stepId is defined.
    queryFn: () => getJobs({ project_id: projectID! }),
    enabled: typeof projectID === "number",
  });
}

export type TJobExecuteResponse = {
  id: number;
  job_id: number;
  name: string;
  run_status: "pending" | "running" | "completed" | "failed";
  executor_type: "local" | "remote";
};

export type TCreateJobExecuteOptions = {
  jobId: string | number;
};

export function executeJob(
  options: TCreateJobExecuteOptions
): Promise<TJobExecuteResponse> {
  const { jobId } = options;
  return api.post({}, `/job/execute?job_id=${jobId}`).json();
}

export type TUseExecuteJobOptions = {
  jobId: string | number;
  onError: (error: unknown) => void;
  onSuccess: (data: TJobExecuteResponse) => void;
};

export function useExecuteJob(options: TUseExecuteJobOptions) {
  const { jobId, onError, onSuccess } = options;

  return useMutation({
    mutationFn: () => executeJob({ jobId }),
    onError,
    onSuccess,
  });
}

export type TUpdateJobOptions = {
  job: TJob;
};

export function updateJob(options: TUpdateJobOptions): Promise<TJob> {
  const { job } = options;

  return api.put({ ...job }, "/job").json();
}

export type TUseUpdateJobOptions = {
  onError: (error?: unknown) => void;
  onSuccess: (data: TJob) => void;
};

export function useUpdateJob(options: TUseUpdateJobOptions) {
  const { onError, onSuccess } = options;

  return useMutation({
    mutationFn: updateJob,
    onError,
    onSuccess,
  });
}
