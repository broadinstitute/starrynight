import { Download } from "lucide-react";
import { Modal } from "../modal";
import { Button } from "@/components/ui/button";
import React from "react";
import { FileViewerMain } from "./main";
import { FileViewerStoreProvider } from "./provider";
import { PageSpinner } from "../page-spinner";
import { TCreateFileViewerStoreOptions } from "./store";
import { TFileType } from "@/utils/file";
import {
  TUseProcessFileOrURLData,
  useProcessFileOrURL,
} from "./useProcessFileOrURL";
import { downloadFile } from "@/utils/download";

export type TFileViewerProps = {
  /**
   * URL where to look for the file.
   */
  url?: string;
  /**
   * Local file to be displayed.
   */
  file?: File;
  /**
   * Element that will trigger the modal/viewer to open.
   */
  trigger: React.ReactNode;
};

export function FileViewer(props: TFileViewerProps) {
  const { url, file, trigger } = props;
  const [storeOptions, setStoreOptions] =
    React.useState<TCreateFileViewerStoreOptions>();

  const [canDownloadFile, setCanDownloadFile] = React.useState(false);

  const handleOnProcessFileSuccess = React.useCallback(
    (data: TUseProcessFileOrURLData, fileType: TFileType, name: string) => {
      if (
        (
          [
            "csv",
            "jpg",
            "json",
            "parquet",
            "png",
            "tsv",
            "txt",
            "xml",
            "yml",
            "cppipe",
          ] as TFileType[]
        ).includes(fileType)
      ) {
        setCanDownloadFile(true);
      } else {
        setCanDownloadFile(false);
      }

      if (fileType === "notebook") {
        return setStoreOptions({
          iframeViewerOption: {
            src: data as string,
          },
          fileType,
          name,
        });
      }

      if (fileType === "s3-directory") {
        return setStoreOptions({
          s3DirectoryViewerOption: {
            url: data as string,
          },
          fileType,
          name,
        });
      }

      return setStoreOptions({
        fileType,
        name,
        bufferViewerOption: {
          data: data as ArrayBuffer,
        },
      });
    },
    []
  );

  const handleOnProcessFileError = React.useCallback(() => {
    console.error("Failed to process file or url.");
  }, []);

  const { processFileOrURL } = useProcessFileOrURL({
    onError: handleOnProcessFileError,
    onSuccess: handleOnProcessFileSuccess,
    file,
    url,
  });

  const handleDownload = React.useCallback(() => {
    if (!storeOptions?.bufferViewerOption) return;

    downloadFile({
      content: storeOptions.bufferViewerOption.data,
      filename: storeOptions.name,
    });
  }, [storeOptions]);

  React.useEffect(() => {
    processFileOrURL();
  }, [processFileOrURL]);

  return (
    <Modal
      contentProps={{
        className:
          "sm:max-w-[95vw] md:max-w-[95vw] xl:max-w-[1250px] h-[95vh] max-h-[800px] flex flex-col gap-0",
      }}
      headerProps={{
        className: "mb-0",
      }}
      title="File Viewer"
      trigger={trigger}
      hasCloseButtonInFooter
      actions={
        canDownloadFile
          ? [
              <Button variant="default" key="download" onClick={handleDownload}>
                <Download /> Download
              </Button>,
            ]
          : []
      }
    >
      {!storeOptions ? (
        <PageSpinner />
      ) : (
        <FileViewerStoreProvider options={storeOptions}>
          <FileViewerMain />
        </FileViewerStoreProvider>
      )}
    </Modal>
  );
}
