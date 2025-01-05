import React from "react";
import { FileViewerCSVLike } from "./csv";
import { FileViewerMessage } from "./message";
import { useDimension } from "@/hooks/useDimension";
import { useFileViewerStore } from "./provider";
import { PageSpinner } from "../page-spinner";
import { FileViewerParquet } from "./parquet";
import { FileViewerText } from "./text";

export function FileViewerViewerSection() {
  const { fileType } = useFileViewerStore((store) => ({
    fileType: store.fileType,
  }));

  const ref = React.useRef<HTMLDivElement>(null);
  const { width, height } = useDimension({ ref });

  const Renderer = React.useMemo(() => {
    if (!width || !height) return <PageSpinner />;

    switch (fileType) {
      case "csv":
      case "tsv":
        return <FileViewerCSVLike parentDimension={[width, height]} />;
      case "parquet":
        return <FileViewerParquet parentDimension={[width, height]} />;
      case "txt":
      case "json":
      case "yml":
      case "xml":
        return <FileViewerText parentDimension={[width, height]} />;
      default:
        return (
          <FileViewerMessage message="A viewer for this file is not available. Please download the file to view it locally." />
        );
    }
  }, [fileType, width, height]);

  return (
    <div ref={ref} className="flex flex-1">
      {Renderer}
    </div>
  );
}
