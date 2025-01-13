import { TJob } from "@/services/job";
import { useParsePathRecordToArray } from "../hooks/useParsePathRecordToArray";
import React from "react";
import { ProjectJobInput } from "./job-input";

export type TProjectJobInputsProps = {
  job: TJob;
};

export function ProjectJobInputs(props: TProjectJobInputsProps) {
  const { job } = props;
  const inputs = useParsePathRecordToArray({ records: job.spec.inputs });

  return (
    <div className="flex-1">
      <h5 className="font-bold">Inputs</h5>
      {inputs.length === 0 && (
        <p className="text-sm text-gray-400 my-2">This job has no input</p>
      )}
      <div className="space-y-2 my-2">
        {inputs.map((input) => (
          <ProjectJobInput input={input} key={input.id} />
        ))}
      </div>
    </div>
  );
}
