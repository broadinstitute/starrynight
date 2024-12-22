import { useQuery } from "@tanstack/react-query";
import { api } from "./api";

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
  outputs: Record<string, TJobOutput>;
  inputs: Record<string, TJobInput>;
};

export type TGetJobsOptions = {
  stepId: string | number;
};

export function getJobs(options: TGetJobsOptions): Promise<TJob[]> {
  const { stepId } = options;
  return api.get(`/job/?step_id=${stepId}`).json();
}

export const GET_JOBS_QUERY_KEY = "GET_JOBS_QUERY_KEY";

export type TUseGetJobsOptions = {
  stepId?: string | number;
};

export function useGetJobs(options: TUseGetJobsOptions) {
  const { stepId } = options;

  return useQuery({
    queryKey: [GET_JOBS_QUERY_KEY, stepId],
    // queryFn will only run if stepId is defined.
    queryFn: () => getJobs({ stepId: stepId! }),
    enabled: typeof stepId === "number" || typeof stepId === "string",
  });
}

export type TJobExecuteResponse = {};

export type TCreateJobExecuteOptions = {
  jobId: string | number;
};

export function executeJob(
  options: TCreateJobExecuteOptions
): Promise<TJobExecuteResponse> {
  const { jobId } = options;
  return api.post({}, `/job/execute?job_id=${jobId}`).json();
}

export type TUpdateJobOptions = {
  job: TJob;
};

export function updateJob(options: TUpdateJobOptions) {
  const { job } = options;

  return api.put({ ...job }, "/job").json();
}
