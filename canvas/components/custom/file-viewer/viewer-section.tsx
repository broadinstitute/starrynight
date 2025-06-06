import React from "react";
import { FileViewerCSVLike } from "./csv";
import { FileViewerMessage } from "./message";
import { useDimension } from "@/hooks/useDimension";
import { useFileViewerStore } from "./provider";
import { PageSpinner } from "../page-spinner";
import { FileViewerParquet } from "./parquet";
import { FileViewerText } from "./text";
import { FileViewerListFiles } from "./list-files";
import { FileViewerNotebook } from "./notebook-viewer";

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
      case "cppipe":
        return <FileViewerText parentDimension={[width, height]} />;
      case "s3-directory":
        return <FileViewerListFiles parentDimension={[width, height]} />;
      case "notebook":
        return <FileViewerNotebook parentDimension={[width, height]} />;
      default:
        return (
          <FileViewerMessage message="A viewer for this file/directory is not available." />
        );
    }
  }, [fileType, width, height]);

  return (
    <div ref={ref} className="flex flex-1">
      {Renderer}
    </div>
  );
}
