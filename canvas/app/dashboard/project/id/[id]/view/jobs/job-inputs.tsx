import { TJob } from "@/services/job";
import { useParseJobInput } from "./useParseJobInput";
import React from "react";
import { ProjectJobInput } from "./job-input";

export type TProjectJobInputsProps = {
  job: TJob;
};

export function ProjectJobInputs(props: TProjectJobInputsProps) {
  const { job } = props;
  const { inputs } = useParseJobInput({ job });

  return (
    <div className="flex-1">
      <h5 className="font-bold">Inputs</h5>
      {inputs.length === 0 && (
        <p className="text-sm text-gray-400 my-2">This job has no input</p>
      )}
      <ul className="space-y-2 my-2">
        {inputs.map((input) => (
          <ProjectJobInput input={input} key={input.id} />
        ))}
      </ul>
    </div>
  );
}
