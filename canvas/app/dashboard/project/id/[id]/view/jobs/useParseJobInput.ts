import { TJob } from "@/services/job";
import { useProjectStore } from "@/stores/project";
import React from "react";

export type TUseParseJobInputOptions = {
  job: TJob;
};

export type TUseParseJobInput = {
  id: string;
  /**
   * Name of the input
   */
  name: string;
  /**
   * Type of input.
   */
  type: "path";
  /**
   * Full path.
   */
  value: string;
  /**
   * Workspace path.
   */
  workspaceURI: string;
  /**
   * Sub path.
   */
  subPath: string;
};

export type TUseParseJobInputReturn = {
  inputs: TUseParseJobInput[];
};

export function useParseJobInput(
  options: TUseParseJobInputOptions
): TUseParseJobInputReturn {
  const { job } = options;
  const { projectWorkspaceURI } = useProjectStore((state) => ({
    projectWorkspaceURI: state.project.workspace_uri,
  }));

  const inputs = React.useMemo((): TUseParseJobInput[] => {
    const _inputs = [] as TUseParseJobInput[];

    for (const [key, value] of Object.entries(job.inputs)) {
      const workspaceURI = projectWorkspaceURI.replace(/\/$/, ""); // Remove trailing slash.
      const subPath = value.value.replace(/\/$/, "").replace(workspaceURI, "");

      _inputs.push({
        id: key,
        name: key,
        type: value.type as "path",
        workspaceURI,
        subPath,
        value: `${workspaceURI}${subPath}`,
      });
    }

    return _inputs;
  }, [job, projectWorkspaceURI]);

  return {
    inputs,
  };
}
