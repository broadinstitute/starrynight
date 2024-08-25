"use client";

import { TProjectStepJob } from "@/services/job";
import { TProjectStepJobRun } from "@/services/run";
import React from "react";
import { ProjectStepJobRun } from "./run";
import { RunsActions } from "./runs-actions";

export type TProjectStepJobRunProps = {
  runs: TProjectStepJobRun[];
  job: TProjectStepJob;
  mutateKey: string;
};

export function ProjectStepJobRuns(props: TProjectStepJobRunProps) {
  const { runs, job, mutateKey } = props;

  return (
    <div>
      <div className="flex justify-between">
        <p className="pt-2">{job.description}</p>
        <div>
          <RunsActions job={job} mutateKey={mutateKey} />
        </div>
      </div>
      {runs.map((run, idx) => (
        <div key={run.id}>
          <ProjectStepJobRun run={run} />
          {idx !== runs.length - 1 && <hr className="my-4" />}
        </div>
      ))}
      {runs.length === 0 && <p className="mb-4">No job is running.</p>}
    </div>
  );
}
