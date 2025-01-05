import React from "react";

import { ViewFile } from "../view-file";
import { formatFileSize, getFileIcon } from "./util";

export type TFileDisplayProps = {
  file: File;
  hasViewFileAction?: boolean;
};

export function FileDisplay(props: TFileDisplayProps) {
  const { file, hasViewFileAction = true } = props;

  return (
    <div className="flex items-center space-x-4 p-4 border border-gray-200 rounded-md shadow-sm">
      <div>{getFileIcon(file.type)}</div>

      <div className="flex-1">
        <p className="max-w-56 text-sm font-medium text-gray-800 truncate">
          {file.name}
        </p>
        <p className="text-xs text-gray-500">{formatFileSize(file.size)}</p>
      </div>
      {hasViewFileAction && <ViewFile file={file} />}
    </div>
  );
}
