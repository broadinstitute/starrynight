import React from "react";
import { useParseCSVBuffer } from "./useParseCSVBuffer";
import { FileViewerMessage } from "../message";
import { PageSpinner } from "../../page-spinner";
import { FileViewerTableView } from "../table-view";

export type TFileViewerCSVLikeProps = {
  /**
   * Width and height of parent element.
   */
  parentDimension: [number, number];
};

/**
 * A component to view CSV like files in a table format.
 */
export function FileViewerCSVLike(props: TFileViewerCSVLikeProps) {
  const { parentDimension } = props;
  const { rows, header, hasError, isDone } = useParseCSVBuffer();

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
