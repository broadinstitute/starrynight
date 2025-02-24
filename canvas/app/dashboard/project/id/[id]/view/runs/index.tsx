import { TJob } from "@/services/job";
import { useGetRuns } from "@/services/run";
import { PlayIcon } from "lucide-react";
import { ProjectRun } from "./run";
import { useProjectStore } from "@/stores/project";
import React from "react";

export type TProjectRunProps = {
  job: TJob;
};

export function ProjectRuns(props: TProjectRunProps) {
  const { job } = props;
  const { updateJobStatus } = useProjectStore((store) => ({
    updateJobStatus: store.updateJobStatus,
  }));

  const { data, isLoading, error } = useGetRuns({ jobId: job.id });

  React.useEffect(() => {
    if (data && data.length > 0) {
      updateJobStatus(job.id, data[data.length - 1].run_status);
    }
  }, [data, job.id, updateJobStatus]);

  if (isLoading) {
    return <p>Loading...</p>;
  }

  if (error || !data) {
    return (
      <p className="text-red-500 text-sm">Failed to load job&lsquo;s run </p>
    );
  }

  return (
    <div className="h-96 overflow-auto">
      <h5 className="font-bold mb-1">Runs</h5>
      {data.length === 0 && (
        <div className="text-sm text-gray-400">
          Click the play button (<PlayIcon className="h-4 w-4 inline-flex" />)
          to run this job. Once started, a Run will be displayed here.
        </div>
      )}

      <ul className="space-y-3 mt-2">
        {data.map((run) => (
          <li key={run.id}>
            <ProjectRun run={run} />
          </li>
        ))}
      </ul>
    </div>
  );
}
