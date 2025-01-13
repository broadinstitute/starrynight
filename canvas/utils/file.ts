import { getFile } from "@/services/s3";
import { useQuery } from "@tanstack/react-query";

export type TFileType =
  | "csv"
  | "tsv"
  | "txt"
  | "yml"
  | "json"
  | "xml"
  | "parquet"
  | "jpg"
  | "png"
  | "notebook"
  | "s3-directory"
  | "not-supported";

export type TGetFileTypeFile = string | File;

export function getNotebookFilename(url: string) {
  /**
   * It should start with http
   */
  if (!url.startsWith("http")) return "";
  try {
    const _url = new URL(url);
    const searchParams = new URLSearchParams(_url.search);

    const file = searchParams.get("file");

    if (!file) return "";

    return file;
  } catch (error) {
    console.error(error);
    return "";
  }
}

/**
 * Return true if the url is a notebook path.
 */
export function isNotebookURL(url: string): boolean {
  const filename = getNotebookFilename(url);

  if (filename.endsWith(".py")) {
    return true;
  }

  return false;
}

export function isS3DirectoryURL(url: string): boolean {
  try {
    const _url = new URL(url);
    if (_url.hostname === "s3.amazonaws.com") {
      return true;
    }
  } catch (error) {
    console.error(error);
  }
  return false;
}

/**
 * Return the type of file from a given file or file path or url.
 */
export function getFileType(file: TGetFileTypeFile): TFileType {
  if (!file || (typeof file !== "string" && !(file instanceof File))) {
    throw new Error("Invalid file or path");
  }

  if (typeof file === "string" && isNotebookURL(file)) {
    return "notebook";
  }

  const extension =
    file instanceof File
      ? file.name.split(".").pop()?.toLowerCase()
      : file.split(".").pop()?.toLowerCase();

  if (!extension) {
    if (typeof file === "string" && isS3DirectoryURL(file)) {
      return "s3-directory";
    }

    console.warn("Unable to resolve file type.", file);
    return "not-supported";
  }

  switch (extension) {
    // ---------> Tabular
    case "parquet":
      return "parquet";
    case "csv":
      return "csv";
    case "tsv":
      return "tsv";
    case "xml":
      return "xml";

    // ---------> Text
    case "txt":
      return "txt";
    case "json":
      return "json";
    case "yml":
      return "yml";

    // ---------> Images
    case "jpg":
      return "jpg";
    case "jpeg":
      return "jpg";
    case "png":
      return "png";

    // ---------> Others
    default:
      return "not-supported";
  }
}

export function getFileName(file: TGetFileTypeFile): string {
  if (file instanceof File) {
    return file.name;
  }

  if (isNotebookURL(file)) {
    return getNotebookFilename(file);
  }

  return file.split("/").pop() || "No Filename";
}

export type TUseGetFileOptions = {
  url: string;
  enabled: boolean;
};

export const GET_FILE_QUERY_KEY = "GET_FILE_QUERY_KEY";

export function useGetFile(options: TUseGetFileOptions) {
  const { url, enabled } = options;

  return useQuery({
    queryKey: [GET_FILE_QUERY_KEY, url],
    queryFn: () => getFile(url),
    refetchOnMount: false,
    refetchOnWindowFocus: false,
    enabled,
  });
}
