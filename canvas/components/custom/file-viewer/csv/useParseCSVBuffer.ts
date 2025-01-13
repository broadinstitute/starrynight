import React from "react";
import Papaparse from "papaparse";
import { useFileViewerStore } from "../provider";

const textDecoder = new TextDecoder();

export function useParseCSVBuffer() {
  const { buffer, addDetails } = useFileViewerStore((store) => ({
    buffer: store.bufferViewerOption,
    addDetails: store.addDetails,
  }));

  const [rows, setRows] = React.useState([] as string[][]);
  const [header, setHeader] = React.useState([] as string[]);
  const [isDone, setIsDone] = React.useState(false);
  const [hasError, setHasError] = React.useState(false);

  const processBuffer = React.useCallback(async () => {
    if (!buffer || !buffer.data) return;

    const csvString = textDecoder.decode(buffer.data);
    const parsed = Papaparse.parse(csvString);

    setRows(parsed.data.slice(1) as string[][]);
    setHeader(parsed.data[0] as string[]);

    addDetails([
      ["Row(s)", parsed.data.length - 1],
      ["Column(s)", (parsed.data[0] as string[]).length],
    ]);

    setIsDone(true);
    setHasError(false);
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
