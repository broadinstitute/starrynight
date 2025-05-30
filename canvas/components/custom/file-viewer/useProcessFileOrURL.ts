import {
  getFileName,
  getFileType,
  getNotebookFilename,
  TFileType,
  useGetFile,
} from "@/utils/file";
import React, { useState } from "react";

export type TUseProcessFileOrURLData = ArrayBuffer | string;

export type UseProcessFileOrURLOptions = {
  file?: File;
  url?: string;

  onSuccess: (
    data: TUseProcessFileOrURLData,
    fileType: TFileType,
    fileName: string
  ) => void;
  onError: (error: unknown) => void;
};

export function useProcessFileOrURL(options: UseProcessFileOrURLOptions) {
  const { file, url, onError, onSuccess } = options;

  const [isGetFileEnabled, setIsGetFileEnabled] = useState(false);

  const { data, error, isLoading } = useGetFile({
    enabled: isGetFileEnabled,
    url: url!,
  });

  const handleGetFileSuccessResponse = React.useCallback(async () => {
    if (!data || !url) return;

    const fileName = getFileName(url);
    const filetype = getFileType(url);
    let _buffer: ArrayBuffer;

    if (typeof data === "string") {
      _buffer = await new Blob([data]).arrayBuffer();
    } else if (data instanceof Blob) {
      _buffer = await data.arrayBuffer();
    } else {
      _buffer = data.buffer as ArrayBuffer;
    }

    onSuccess(_buffer, filetype, fileName);
  }, [data, url, onSuccess]);

  React.useEffect(() => {
    if (!isGetFileEnabled || isLoading || !url) return;

    if (error || !data) {
      onError(error);
    }

    handleGetFileSuccessResponse();
  }, [
    isGetFileEnabled,
    data,
    error,
    isLoading,
    url,
    handleGetFileSuccessResponse,
    onError,
  ]);

  const _processFile = React.useCallback(
    async (_file: File) => {
      try {
        const fileType = getFileType(_file);
        const buffer = await _file.arrayBuffer();
        const filename = getFileName(_file);

        onSuccess(buffer, fileType, filename);
      } catch (error) {
        onError(error);
      }
    },
    [onSuccess, onError]
  );

  const _processURL = React.useCallback(
    (_url: string) => {
      // FIXME: using template literal to coerce boolean value to string
      const fileType = getFileType(`${_url}`);

      if (fileType === "notebook") {
        const filename = getNotebookFilename(_url);
        return onSuccess(_url, fileType, filename);
      }

      if (fileType === "s3-directory" || fileType === "not-supported") {
        return onSuccess(`${_url}`, fileType, getFileName(`${_url}`));
      }

      // We need to fetch the file.
      setIsGetFileEnabled(true);
    },
    [onSuccess]
  );

  const processFileOrURL = React.useCallback(() => {
    if (!url && !file) {
      throw new Error("Either 'url' or 'file' must be provided.");
    }

    if (url && file) {
      console.warn(
        "Both `url` and `file` are provided. Using `url` to download and view the file."
      );
    }

    if (file) {
      _processFile(file);
    } else if (url) {
      _processURL(url);
    }
  }, [_processFile, _processURL, file, url]);

  return {
    processFileOrURL,
  };
}
