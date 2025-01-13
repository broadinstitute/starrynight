import React from "react";
import { FileViewerMessage } from "./message";
import { useFileViewerStore } from "./provider";

export type TFileViewerNotebookProps = {
  /**
   * Width and height of parent element.
   */
  parentDimension: [number, number];
};

/**
 * A component to view notebook file in an iFrame.
 */
export function FileViewerNotebook(props: TFileViewerNotebookProps) {
  const { parentDimension } = props;
  const { iframeViewerOption } = useFileViewerStore((store) => ({
    iframeViewerOption: store.iframeViewerOption,
  }));

  if (!iframeViewerOption) {
    return (
      <FileViewerMessage message="An error occurred while attempting to load the notebook into the iFrame." />
    );
  }

  return (
    <iframe
      src={iframeViewerOption.src}
      height={parentDimension[1]}
      width={parentDimension[0]}
    />
  );
}
