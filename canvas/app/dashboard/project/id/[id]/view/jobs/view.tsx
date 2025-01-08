import { TJob } from "@/services/job";
import { ProjectJob } from "./job";

export type TProjectJobsViewProps = {
  jobs: TJob[];
};

export function ProjectJobsView(props: TProjectJobsViewProps) {
  const { jobs } = props;

  return (
    <div>
      <div className="grid grid-cols-1 gap-4 pt-4">
        {jobs.map((job) => (
          <ProjectJob job={job} key={job.id} />
        ))}
      </div>
    </div>
  );
}
