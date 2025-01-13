import { TSpecPathRecord } from "@/services/misc";
import { useProjectStore } from "@/stores/project";
import React from "react";

export type TUseParsePathRecordToArrayOptions = {
  records: TSpecPathRecord[];
};

export type TPathRecord = {
  id: string;
  name: string;
  type: string;
  value: string;
};

export type TUseParsePathRecordToArrayReturn = TPathRecord[];

export function useParsePathRecordToArray(
  options: TUseParsePathRecordToArrayOptions
): TUseParsePathRecordToArrayReturn {
  const { records } = options;
  const { projectWorkspaceURI } = useProjectStore((state) => ({
    projectWorkspaceURI: state.project.workspace_uri,
  }));

  return React.useMemo((): TUseParsePathRecordToArrayReturn => {
    if (!records) return [];

    const out = [] as TUseParsePathRecordToArrayReturn;

    for (const record of records) {
      const { type, name, path } = record;

      out.push({
        id: name,
        name,
        type,
        value: path || projectWorkspaceURI,
      });
    }

    return out;
  }, [projectWorkspaceURI, records]);
}
