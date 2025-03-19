import { TRun } from "@/services/run";
import { ProjectRunBadge } from "./badge";
import { RunPathsPopover } from "./run-paths-popover";
import { useParsePathRecordToArray } from "../hooks/useParsePathRecordToArray";
import { FileInput, FileOutput } from "lucide-react";
import { RunViewLog } from "./view-logs";
import { KillRun } from "./kill-run";

export type TProjectRun = {
  run: TRun;
};

export function ProjectRun(props: TProjectRun) {
  const { run } = props;

  const inputs = useParsePathRecordToArray({ records: run.spec.inputs });
  const outputs = useParsePathRecordToArray({
    records: run.spec.outputs,
  });

  return (
    <div className="border-b border-b-gray-200 text-sm pb-2">
      <div className="font-bold">{run.name}</div>
      <div className="pt-2 inline-flex flex-col md:flex md:flex-row md:justify-between md:items-center">
        <ProjectRunBadge status={run.run_status} />

        <div>
          <KillRun run={run} />
          <RunPathsPopover
            paths={inputs}
            title="Run Inputs"
            noPathsMessage="No input file for this run."
            viewActionTooltipMessage="View input file"
            triggerProps={{ message: "View inputs", children: <FileInput /> }}
          />
          <RunPathsPopover
            paths={outputs}
            title="Run Outputs"
            noPathsMessage="No output file for this run."
            viewActionTooltipMessage="View output file"
            triggerProps={{
              message: "View outputs",
              children: <FileOutput />,
            }}
          />
          <RunViewLog run={run} />
        </div>
      </div>
    </div>
  );
}
