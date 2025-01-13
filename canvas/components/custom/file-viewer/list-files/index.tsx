import React from "react";
import { FileViewerMessage } from "../message";

export type TFileViewerListFilesProps = {
  /**
   * Width and height of parent element.
   */
  parentDimension: [number, number];
};

/**
 * A component to view directory files in a list.
 */
export function FileViewerListFiles(props: TFileViewerListFilesProps) {
  return (
    <FileViewerMessage message="Currently we don't support viewing a directory." />
  );
}
