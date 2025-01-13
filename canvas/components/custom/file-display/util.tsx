import {
  File,
  FileText,
  FileImage,
  FileVideo,
  FileAudio,
  FileArchive,
  FileBox,
  FileChartColumn,
  FileJson,
  FileCode,
} from "lucide-react";

export function formatFileSize(size: number) {
  if (size < 1024) return `${size} B`;
  if (size < 1024 * 1024) return `${(size / 1024).toFixed(2)} KB`;
  return `${(size / (1024 * 1024)).toFixed(2)} MB`;
}

const fileTypeRegEx = {
  tabular: /vnd.ms-excel|csv|tsv|parquet/,
  image: /image|jpg|jpeg|png|gif|bmp|webp|svg|ico|tiff?/i,
  video: /video|mp4|mov|wmv|avi|mkv|flv|webm|3gp|ogg|m4v/i,
  audio: /audio|mp3|wav|aac|flac|ogg|m4a|wma/i,
  text: /text|txt|md|json|xml|yml/i,
  archive: /application\/(zip|x-rar-compressed)/,
};

export function getFileIcon(fileType: string) {
  const { tabular, image, video, audio, text, archive } = fileTypeRegEx;

  if (image.test(fileType))
    return <FileImage className="w-6 h-6 text-blue-500" />;
  if (video.test(fileType))
    return <FileVideo className="w-6 h-6 text-red-500" />;
  if (audio.test(fileType))
    return <FileAudio className="w-6 h-6 text-purple-500" />;
  if (archive.test(fileType))
    return <FileArchive className="w-6 h-6 text-yellow-500" />;
  if (text.test(fileType)) {
    if (fileType.includes("json"))
      return <FileJson className="w-6 h-6 text-yellow-500" />;
    if (fileType.includes("yml"))
      return <FileCode className="w-6 h-6 text-purple-500" />;
    if (fileType.includes("xml"))
      return <FileCode className="w-6 h-6 text-green-500" />;
    return <FileText className="w-6 h-6 text-blue-500" />;
  }
  if (tabular.test(fileType)) {
    return <FileChartColumn className="w-6 h-6 text-green-500" />;
  }

  if (fileType.includes("pdf")) {
    return <FileText className="w-6 h-6 text-red-500" />;
  }
  if (fileType.startsWith("application/"))
    return <FileBox className="w-6 h-6 text-gray-500" />;

  return <File className="w-6 h-6 text-gray-400" />;
}
