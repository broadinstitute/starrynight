import { TJob } from "@/services/job";
import { ProjectJobCard } from "./card";
import { TStep } from "@/services/step";

export type TProjectJobsViewProps = {
  jobs: TJob[];
  step: TStep;
};

export function ProjectJobsView(props: TProjectJobsViewProps) {
  const { jobs, step } = props;

  return (
    <div>
      <h4 className="font-bold text-xl mb-2">{step.name}</h4>
      {step.description && <p className="mb-2">{step.description}</p>}

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        {jobs.map((job) => (
          <ProjectJobCard job={job} key={job.id} />
        ))}
      </div>
    </div>
  );
}
