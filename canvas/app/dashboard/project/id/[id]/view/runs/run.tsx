import { TRun } from "@/services/run";
import { ProjectRunBadge } from "./badge";
import { RunPathsPopover } from "./run-paths-popover";
import { useParsePathRecordToArray } from "../hooks/useParsePathRecordToArray";
import { FileInput, FileOutput, ScrollText } from "lucide-react";
import { ActionButton } from "@/components/custom/action-button";

export type TProjectRun = {
  run: TRun;
};

export function ProjectRun(props: TProjectRun) {
  const { run } = props;

  const inputs = useParsePathRecordToArray({ obj: run.inputs });
  const outputs = useParsePathRecordToArray({
    obj: run.outputs,
    valueKey: "uri",
  });

  return (
    <div className="border-b border-b-gray-200 text-sm pb-2">
      <div className="font-bold">{run.name}</div>
      <div className="pt-2 flex justify-between items-center">
        <ProjectRunBadge status={run.run_status} />

        <div>
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
          <ActionButton icon={<ScrollText />} message="View logs" />
        </div>
      </div>
    </div>
  );
}
