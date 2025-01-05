import React from "react";
import { parquetRead, parquetMetadata, parquetSchema } from "hyparquet";
import { compressors } from "hyparquet-compressors";
import { useFileViewerStore } from "../provider";

export function useParseParquetFile() {
  const { buffer, addDetails } = useFileViewerStore((store) => ({
    buffer: store.buffer,
    addDetails: store.addDetails,
  }));
  const [rows, setRows] = React.useState([] as string[][]);
  const [header, setHeader] = React.useState([] as string[]);
  const [isDone, setIsDone] = React.useState(false);
  const [hasError, setHasError] = React.useState(false);

  const processBuffer = React.useCallback(async () => {
    const { children, count } = parquetSchema(parquetMetadata(buffer));

    try {
      await parquetRead({
        file: buffer,
        compressors,
        onComplete: (data) => {
          setRows(data);
          setHeader(children.map((child) => child.element.name));
          addDetails([
            ["Row(s)", data.length],
            ["Columns", ""],
            ...children.map((child) => {
              return [child.element.name, child.element.type] as [
                string,
                string
              ];
            }),
          ]);
          setIsDone(true);
          setHasError(false);
        },
      });
    } catch (error) {
      console.error("Error while parsing parquet buffer", error);
      setIsDone(true);
      setHasError(true);
    }
  }, [buffer, addDetails]);

  React.useEffect(() => {
    setIsDone(false);
    setHasError(false);
    processBuffer();
  }, [processBuffer]);

  return {
    rows,
    header,
    isDone,
    hasError,
  };
}
