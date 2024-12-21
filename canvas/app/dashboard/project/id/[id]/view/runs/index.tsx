import { TJob } from "@/services/job";
import { useGetRuns } from "@/services/run";
import { PlayIcon } from "lucide-react";
import { ProjectRun } from "./run";

export type TProjectRunProps = {
  job: TJob;
};

export function ProjectRuns(props: TProjectRunProps) {
  const { job } = props;
  const { data, isLoading, error } = useGetRuns({ jobId: job.id });

  if (isLoading) {
    return <p>Loading...</p>;
  }

  if (error || !data || !data.response) {
    return (
      <p className="text-red-500 text-sm">Failed to load job&lsquo;s run </p>
    );
  }

  return (
    <div className="h-96 overflow-auto">
      <h5 className="font-bold mb-1">Runs</h5>
      {data.response.length === 0 && (
        <div className="text-sm text-gray-400">
          Click the play button (<PlayIcon className="h-4 w-4 inline-flex" />)
          to run this job. Once started, a Run will be displayed here.
        </div>
      )}

      {data.response.map((run) => (
        <ProjectRun key={run.id} run={run} />
      ))}
    </div>
  );
}
