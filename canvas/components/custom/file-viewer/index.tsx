import { Download } from "lucide-react";
import { Modal } from "../modal";
import { Button } from "@/components/ui/button";
import React from "react";
import { FileViewerMain } from "./main";
import { FileViewerStoreProvider } from "./provider";
import { PageSpinner } from "../page-spinner";
import { TCreateFileViewerStoreOptions } from "./store";
import { getFileName, getFileType, TFileType } from "@/utils/file";

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
   * If true then download button will be shown.
   */
  hasDownloadButton?: boolean;
  /**
   * Element that will trigger the modal/viewer to open.
   */
  trigger: React.ReactNode;
};

export function FileViewer(props: TFileViewerProps) {
  const { url, file, trigger, hasDownloadButton } = props;
  const [storeOptions, setStoreOptions] =
    React.useState<TCreateFileViewerStoreOptions>();

  if (!url && !file) {
    throw new Error("Either 'url' or 'file' must be provided.");
  }

  if (url && file) {
    console.warn(
      "Both `url` and `file` are provided. Using `url` to download and view the file."
    );
  }

  const createAndSetBuffer = React.useCallback(async () => {
    let _buffer = undefined as undefined | ArrayBuffer;
    let _fileType = "not-supported" as TFileType;
    let _fileName = "";

    if (file) {
      _buffer = await file.arrayBuffer();
      _fileType = getFileType(file);
      _fileName = getFileName(file);
    } else if (url) {
      // TODO: add logic to fetch file.
      _buffer = new ArrayBuffer(0);
      _fileType = getFileType(url);
      _fileName = getFileName(url);
    } else {
      throw new Error("Either 'url' or 'file' must be provided.");
    }

    setStoreOptions({
      buffer: _buffer,
      fileType: _fileType,
      name: _fileName,
    });
  }, [file, url]);

  React.useEffect(() => {
    createAndSetBuffer();
  }, [createAndSetBuffer]);

  const handleDownload = React.useCallback(() => {
    // TODO: Implement download logic here.
  }, []);

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
        hasDownloadButton
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
