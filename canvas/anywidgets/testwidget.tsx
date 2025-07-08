// index.jsx
import * as React from "react";
import { useModelState, createRender } from "@anywidget/react";

import { TJob } from "@/services/job";
import { useParsePathRecordToArray } from "../app/dashboard/project/id/[id]/view/hooks/useParsePathRecordToArray";
import { ProjectJobInput } from "../app/dashboard/project/id/[id]/view/jobs/job-input";

export type TProjectJobInputsProps = {
  job: TJob;
};

function ModuleView() {
  let [spec, setSpec] = useModelState("spec");
  // return (
  // <div>
  //     <h1>Spec</h1>
  //     <button onClick={ () => setSpec({...spec, "cli_tag": "thisisajsvalue"})}>
  //       Change a value
  //     </button>
  //     <div className="px-1.5 py-2 bg-accent text-accent-foreground rounded-md">
  //       {"inputName"}
  //     </div>
  //     <span>{JSON.stringify(spec)}</span>
  // </div>
  // ); 
  return (
    <div className="flex-1">
      <h5 className="font-bold">Inputs</h5>
      {inputs.length === 0 && (
        <p className="text-sm text-gray-400 my-2">This job has no input</p>
      )}
      <div className="space-y-2 my-2">
        {spec["inputs"].map((input) => (
          <ProjectJobInput job={spec} input={input} key={input["id"]} />
        ))}
      </div>
    </div>
  );
}

export default {
  render: createRender(ModuleView)
};
