import React from "react";
import {
  File,
  FileText,
  FileImage,
  FileVideo,
  FileAudio,
  FileCode,
  FileArchive,
  FileSpreadsheet,
} from "lucide-react";
import { ViewFile } from "./view-file";

export type TFileDisplayProps = {
  file: File;
};

export function FileDisplay(props: TFileDisplayProps) {
  const { file } = props;

  return (
    <div className="flex items-center space-x-4 p-4 border border-gray-200 rounded-md shadow-sm">
      <div>{getFileIcon(file.type)}</div>

      <div className="flex-1">
        <p className="max-w-56 text-sm font-medium text-gray-800 truncate">
          {file.name}
        </p>
        <p className="text-xs text-gray-500">{formatFileSize(file.size)}</p>
      </div>
      <ViewFile file={file} />
    </div>
  );
}

function formatFileSize(size: number) {
  if (size < 1024) return `${size} B`;
  if (size < 1024 * 1024) return `${(size / 1024).toFixed(2)} KB`;
  return `${(size / (1024 * 1024)).toFixed(2)} MB`;
}

function getFileIcon(fileType: string) {
  if (fileType.startsWith("image/"))
    return <FileImage className="w-6 h-6 text-blue-500" />;
  if (fileType.startsWith("video/"))
    return <FileVideo className="w-6 h-6 text-red-500" />;
  if (fileType.startsWith("audio/"))
    return <FileAudio className="w-6 h-6 text-purple-500" />;
  if (
    fileType === "application/zip" ||
    fileType === "application/x-rar-compressed"
  )
    return <FileArchive className="w-6 h-6 text-yellow-500" />;
  if (fileType.startsWith("text/"))
    return <FileText className="w-6 h-6 text-green-500" />;
  if (fileType.includes("vnd.ms-excel")) {
    return <FileSpreadsheet className="w-6 h-6 text-green-500" />;
  }

  if (fileType.includes("pdf")) {
    return <FileText className="w-6 h-6 text-red-500" />;
  }
  if (fileType.startsWith("application/"))
    return <FileCode className="w-6 h-6 text-gray-500" />;
  return <File className="w-6 h-6 text-gray-400" />;
}
