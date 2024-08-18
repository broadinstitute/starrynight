import { api, TResponse } from "./api";

export type TProjectStepJobRun = {
  id: string | number;
  job_id: string | number;
  name: string;
};

export type TGetStepJobsRunOptions = {
  canThrowOnError?: boolean;
  job_id: string | number;
};

export async function getRun(
  options: TGetStepJobsRunOptions
): Promise<TResponse<TProjectStepJobRun[]>> {
  const { job_id, canThrowOnError } = options;
  try {
    const response = (await api
      .get(`/run/?job_id=${job_id}`)
      .json()) as TProjectStepJobRun[];

    return {
      ok: true,
      response,
    };
  } catch (error) {
    console.error(error);

    if (canThrowOnError) {
      throw new Error("Error while fetching job run");
    }

    return {
      error,
    };
  }
}

export type TCreateStepJobsRunOptions = {
  canThrowOnError?: boolean;
  id: string | number;
  jobId: string | number;
  name: string;
};

export async function createRun(
  options: TCreateStepJobsRunOptions
): Promise<TResponse<TProjectStepJobRun>> {
  const { jobId, name, id, canThrowOnError } = options;
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
      .json()) as TProjectStepJobRun;

    return {
      ok: true,
      response,
    };
  } catch (error) {
    console.error(error);

    if (canThrowOnError) {
      throw new Error("Error while creating job run");
    }

    return {
      error,
    };
  }
}
