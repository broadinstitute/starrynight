import { TRun } from "@/services/run";

export type TProjectRun = {
  run: TRun;
};

export function ProjectRun(props: TProjectRun) {
  const { run } = props;

  return (
    <div>
      {run.name} - {run.run_status} - {run.id}
    </div>
  );
}
