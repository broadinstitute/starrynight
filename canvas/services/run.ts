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

export type TGetRunOptions = {
  canThrowOnError?: boolean;
  job_id: string | number;
};

export async function getRun(
  options: TGetRunOptions
): Promise<TResponse<TRun[]>> {
  const { job_id, canThrowOnError } = options;
  try {
    const response = (await api.get(`/run/?job_id=${job_id}`).json()) as TRun[];

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

export type TCreateRunOptions = {
  canThrowOnError?: boolean;
  id: string | number;
  jobId: string | number;
  name: string;
};

export async function createRun(
  options: TCreateRunOptions
): Promise<TResponse<TRun>> {
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
      .json()) as TRun;

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
