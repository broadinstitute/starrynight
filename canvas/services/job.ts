import { api, TResponse } from "./api";

export type TProjectStepJobOutput = {
  type: string;
  uri: string;
};

export type TProjectStepJob = {
  id: string | number;
  step_id: string | number;
  name: string;
  description: string;
  type: string;
  outputs: Record<string, TProjectStepJobOutput>;
};

export type TGetStepJobsOptions = {
  canThrowOnError?: boolean;
  stepId: string | number;
};

export async function getJobs(
  options: TGetStepJobsOptions
): Promise<TResponse<TProjectStepJob[]>> {
  const { stepId, canThrowOnError } = options;
  try {
    const response = (await api
      .get(`/job/?step_id=${stepId}`)
      .json()) as TProjectStepJob[];

    return {
      ok: true,
      response,
    };
  } catch (error) {
    console.error(error);

    if (canThrowOnError) {
      throw new Error("Error while fetching jobs");
    }

    return {
      error,
    };
  }
}

export type TProjectStepJobExecuteResponse = {};

export type TCreateStepJobsExecuteOptions = {
  canThrowOnError?: boolean;
  jobId: string | number;
};

export async function executeJob(
  options: TCreateStepJobsExecuteOptions
): Promise<TResponse<TProjectStepJobExecuteResponse>> {
  const { jobId, canThrowOnError } = options;
  try {
    const response = (await api
      .post({}, `/job/execute?job_id=${jobId}`)
      .json()) as TProjectStepJobExecuteResponse;

    return {
      ok: true,
      response,
    };
  } catch (error) {
    console.error(error);

    if (canThrowOnError) {
      throw new Error("Error while executing the job");
    }

    return {
      error,
    };
  }
}
