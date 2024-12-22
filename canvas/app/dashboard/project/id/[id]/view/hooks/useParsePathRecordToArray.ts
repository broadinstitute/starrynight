import { TJob } from "@/services/job";
import { useProjectStore } from "@/stores/project";
import React from "react";

export type TUseParsePathRecordToArrayOptions<
  T extends Record<string, string>
> = {
  obj: Record<string, T>;
  /**
   * @default "type"
   */
  typeKey?: string;
  /**
   * @default "value"
   */
  valueKey?: string;
};

export type TPathRecord = {
  id: string;
  name: string;
  type: string;
  value: string;
};
export type TUseParsePathRecordToArrayReturn = TPathRecord[];

export function useParsePathRecordToArray<T extends Record<string, string>>(
  options: TUseParsePathRecordToArrayOptions<T>
): TUseParsePathRecordToArrayReturn {
  const { obj, typeKey = "type", valueKey = "value" } = options;
  const { projectWorkspaceURI } = useProjectStore((state) => ({
    projectWorkspaceURI: state.project.workspace_uri,
  }));

  return React.useMemo((): TUseParsePathRecordToArrayReturn => {
    if (!obj) return [];

    const out = [] as TUseParsePathRecordToArrayReturn;

    for (const [k, v] of Object.entries(obj)) {
      const type = v[typeKey];
      const value = v[valueKey] || projectWorkspaceURI;

      out.push({
        id: k,
        name: k,
        type,
        value,
      });
    }

    return out;
  }, [obj, projectWorkspaceURI, typeKey, valueKey]);
}
