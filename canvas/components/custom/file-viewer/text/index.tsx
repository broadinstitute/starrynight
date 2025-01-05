import clsx from "clsx";
import { PageSpinner } from "../../page-spinner";
import { FileViewerMessage } from "../message";
import { useParseTextBuffer } from "./useParseTextBuffer";

export type TFileViewerTextProps = {
  /**
   * Width and height of parent element.
   */
  parentDimension: [number, number];
};

export function FileViewerText(props: TFileViewerTextProps) {
  const { parentDimension } = props;
  const { data, hasError, isDone, fileType } = useParseTextBuffer();

  if (!isDone) {
    return <PageSpinner />;
  }

  if (hasError) {
    return (
      <FileViewerMessage
        message="Something went wrong during parsing the file. Please download the file to
        view it locally."
      />
    );
  }

  return (
    <div
      className="bg-accent p-2 flex"
      style={{ height: parentDimension[1], width: parentDimension[0] }}
    >
      <div
        className={clsx(
          "py-2 px-4 bg-white border border-gray-100 rounded flex-1 overflow-auto",
          fileType !== "txt" && "whitespace-pre"
        )}
      >
        {data}
      </div>
    </div>
  );
}
