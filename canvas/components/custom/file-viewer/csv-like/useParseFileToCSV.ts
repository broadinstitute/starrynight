import React from "react";
import Papaparse from "papaparse";

export type TUseParseFileToCSVOptions = {
  file: File;
};

export function useParseFileToCSV(options: TUseParseFileToCSVOptions) {
  const { file } = options;

  const [rows, setRows] = React.useState([] as string[][]);
  const [header, setHeader] = React.useState([] as string[]);
  const [isDone, setIsDone] = React.useState(false);
  const [hasError, setHasError] = React.useState(false);

  const handleOnFile = React.useCallback(async () => {
    const fileReader = new FileReader();

    fileReader.onload = (event) => {
      const csvString = event.target?.result as string;
      const parsed = Papaparse.parse(csvString);

      setRows(parsed.data.slice(1) as string[][]);
      setHeader(parsed.data[0] as string[]);

      setIsDone(true);
      setHasError(false);
    };

    fileReader.onerror = () => {
      setIsDone(true);
      setHasError(true);
    };

    fileReader.readAsText(file);
  }, [file]);

  React.useEffect(() => {
    if (file) {
      setIsDone(false);
      setHasError(false);
      handleOnFile();
    }
  }, [handleOnFile, file]);

  return {
    rows,
    header,
    isDone,
    hasError,
  };
}
