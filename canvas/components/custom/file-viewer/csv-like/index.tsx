import React from "react";
import { useParseFileToCSV } from "./useParseFileToCSV";
import { FileViewerMessage } from "../message";
import { PageSpinner } from "../../page-spinner";
import { FileViewerTableView } from "../table-view";

export type TFileViewerCSVLikeProps = {
  file: File;
  /**
   * Width and height of parent element.
   */
  parentDimension: [number, number];
};

/**
 * A component to view CSV like files in a table format.
 */
export function FileViewerCSVLike(props: TFileViewerCSVLikeProps) {
  const { file, parentDimension } = props;
  const { rows, header, hasError, isDone } = useParseFileToCSV({ file });

  if (hasError) {
    return (
      <FileViewerMessage
        message="Something went wrong during parsing the file. Please download the file to
        view it locally."
      />
    );
  }

  if (!isDone || !parentDimension[0]) {
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
