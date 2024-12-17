import { TJob } from "@/services/job";
import { ProjectJobInput } from "./inputs";
import { ProjectJobRun } from "./run-job";

export type TProjectJobCardProps = {
  job: TJob;
};

export function ProjectJobCard(props: TProjectJobCardProps) {
  const { job } = props;

  return (
    <div className="p-2 rounded-md border border-accent">
      <div className="flex justify-between">
        <h5 className="font-semibold">{job.name}</h5>
        <div>
          <ProjectJobInput job={job} />
          <ProjectJobRun job={job} />
        </div>
      </div>
      {job.description && <p className="py-2 text-sm">{job.description}</p>}
    </div>
  );
}
