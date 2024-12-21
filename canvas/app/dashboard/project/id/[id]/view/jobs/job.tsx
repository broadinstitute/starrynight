import { TJob } from "@/services/job";
import { ProjectJobRun } from "./run-job";
import { ProjectRuns } from "../runs";
import { ProjectJobInputs } from "./job-inputs";

export type TProjectJobProps = {
  job: TJob;
};

export function ProjectJob(props: TProjectJobProps) {
  const { job } = props;

  return (
    <div className="flex flex-col p-2 rounded-md border border-accent">
      <div className="flex items-center justify-between pb-4 mb-4 border-b border-b-accent">
        <h5 className="font-semibold">{job.name}</h5>
        <div>
          <ProjectJobRun job={job} />
        </div>
      </div>
      <ProjectJobInputs job={job} />
      <hr className="my-4 border-t-accent" />
      {job.description && <p className="py-2 text-sm">{job.description}</p>}
      <ProjectRuns job={job} />
    </div>
  );
}
