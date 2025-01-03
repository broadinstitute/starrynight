import { getFileType } from "@/utils/file";
import React from "react";
import { FileViewerCSVLike } from "./csv-like";
import { FileViewerMessage } from "./message";
import { useDimension } from "@/hooks/useDimension";

export type TFileViewerViewerSectionProps = {
  file: File;
};

export function FileViewerViewerSection(props: TFileViewerViewerSectionProps) {
  const { file } = props;

  const ref = React.useRef<HTMLDivElement>(null);
  const { width, height } = useDimension({ ref });

  const Renderer = React.useMemo(() => {
    const fileType = getFileType(file);
    switch (fileType) {
      case "csv":
      case "tsv":
        return (
          <FileViewerCSVLike parentDimension={[width, height]} file={file} />
        );
      default:
        return (
          <FileViewerMessage message="A viewer for this file is not available. Please download the file to view it locally." />
        );
    }
  }, [file, width, height]);

  return (
    <div ref={ref} className="flex flex-1">
      {Renderer}
    </div>
  );
}
