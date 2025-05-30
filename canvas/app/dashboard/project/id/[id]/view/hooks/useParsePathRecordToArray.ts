import { TSpecPathRecord } from "@/services/misc";
import React from "react";

export type TUseParsePathRecordToArrayOptions = {
  records: Record<string, TSpecPathRecord>;
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

    for (const key in records) {
      const { type, name, value } = records[key];

      out.push({
        id: name,
        name,
        type,
        //FIXME: using string literal to coerce boolean to string
        value: `${value}`,
        raw: records[key],
      });
    }

    return out;
  }, [records]);
}
