import React from "react";
import { useFileViewerStore } from "../provider";
import { countWords } from "@/utils/misc";

const decoder = new TextDecoder();

export function useParseTextBuffer() {
  const { buffer, fileType, addDetails } = useFileViewerStore((store) => ({
    buffer: store.bufferViewerOption,
    addDetails: store.addDetails,
    fileType: store.fileType,
  }));
  const [data, setData] = React.useState("");
  const [isDone, setIsDone] = React.useState(false);
  const [hasError, setHasError] = React.useState(false);

  const parseData = React.useCallback(() => {
    if (!buffer || !buffer.data) {
      return;
    }

    try {
      const string = decoder.decode(buffer.data);

      setData(string);

      if (fileType === "txt") {
        addDetails([
          ["Word Count", countWords(string)],
          ["Character Count", string.length],
        ]);
      }
      setHasError(false);
      setIsDone(true);
    } catch (error) {
      console.error("Error decoding buffer:", error);
      setHasError(true);
      setIsDone(true);
    }
  }, [buffer, addDetails, fileType]);

  React.useEffect(() => {
    setIsDone(false);
    setHasError(false);
    parseData();
  }, [parseData]);

  return {
    data,
    isDone,
    hasError,
    fileType,
  };
}
