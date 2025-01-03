import { Download, Loader2 } from "lucide-react";
import { Modal } from "../modal";
import { Button } from "@/components/ui/button";
import React from "react";
import { PageSpinner } from "../page-spinner";
import { FileViewerMessage } from "./message";
import { FileViewerMain } from "./main";

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

  if (!url && !file) {
    throw new Error("Either 'url' or 'file' must be provided.");
  }

  if (url && file) {
    console.warn(
      "Both `url` and `file` are provided. Using `url` to download and view the file."
    );
  }

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
      actions={[
        <Button variant="default" key="download" onClick={handleDownload}>
          <Download /> Download
        </Button>,
      ]}
    >
      {/* <FileViewerMessage message="We don't support viewing .csv file type yet! Please download it to view." /> */}
      {/* <PageSpinner className="p-16" /> */}
      {file && <FileViewerMain file={file} />}
    </Modal>
  );
}
