import { TSpecPathRecord } from "@/services/misc";
import React from "react";

export type TUseParsePathRecordToArrayOptions = {
  records: TSpecPathRecord[];
};

export type TPathRecord = {
  id: string;
  name: string;
  type: string;
  value: string;
  raw: TSpecPathRecord;
};

export type TUseParsePathRecordToArrayReturn = TPathRecord[];

export function useParsePathRecordToArray(
  options: TUseParsePathRecordToArrayOptions
): TUseParsePathRecordToArrayReturn {
  const { records } = options;

  return React.useMemo((): TUseParsePathRecordToArrayReturn => {
    if (!records) return [];

    const out = [] as TUseParsePathRecordToArrayReturn;

    for (const record of records) {
      const { type, name, path } = record;

      out.push({
        id: name,
        name,
        type,
        value: path,
        raw: record,
      });
    }

    return out;
  }, [records]);
}
