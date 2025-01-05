import React from "react";
import { useParseParquetBuffer } from "./useParseParquetBuffer";
import { FileViewerMessage } from "../message";
import { PageSpinner } from "../../page-spinner";
import { FileViewerTableView } from "../table-view";

export type TFileViewerParquetProps = {
  /**
   * Width and height of parent element.
   */
  parentDimension: [number, number];
};

/**
 * A component to view parquet files in a table format.
 */
export function FileViewerParquet(props: TFileViewerParquetProps) {
  const { parentDimension } = props;
  const { rows, header, hasError, isDone } = useParseParquetBuffer();

  if (hasError) {
    return (
      <FileViewerMessage
        message="Something went wrong during parsing the file. Please download the file to
        view it locally."
      />
    );
  }

  if (!isDone) {
    return <PageSpinner />;
  }

  return (
    <FileViewerTableView
      parentDimension={parentDimension}
      rows={rows}
      header={header}
    />
  );
}
