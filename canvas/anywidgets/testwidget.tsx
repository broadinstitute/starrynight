// index.jsx
import * as React from "react";
import { useModelState, createRender } from "@anywidget/react";

function ModuleView() {
  let [spec, setSpec] = useModelState("spec");
  return (
  <div>
      <h1>Spec</h1>
      <button onClick={ () => setSpec({...spec, "cli_tag": "thisisajsvalue"})}>
        Change a value
      </button>
      <div className="px-1.5 py-2 bg-accent text-accent-foreground rounded-md">
        {"inputName"}
      </div>
      <span>{JSON.stringify(spec)}</span>
  </div>
  ); 
}

export default {
  render: createRender(ModuleView)
};
