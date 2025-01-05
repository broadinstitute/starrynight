import React from "react";
import { useParseParquetFile } from "./useParseParquetFile";
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
 * A component to view CSV like files in a table format.
 */
export function FileViewerParquet(props: TFileViewerParquetProps) {
  const { parentDimension } = props;
  const { rows, header, hasError, isDone } = useParseParquetFile();

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
