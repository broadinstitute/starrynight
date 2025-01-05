export type TFileType =
  | "csv"
  | "tsv"
  | "txt"
  | "parquet"
  | "jpg"
  | "png"
  | "not-supported";

export type TGetFileTypeFile = string | File;

/**
 * Return the type of file from a given file or file path or url.
 */
export function getFileType(file: TGetFileTypeFile): TFileType {
  if (!file || (typeof file !== "string" && !(file instanceof File))) {
    throw new Error("Invalid file or path");
  }

  const extension =
    file instanceof File
      ? file.name.split(".").pop()?.toLowerCase()
      : file.split(".").pop()?.toLowerCase();

  if (!extension) {
    console.warn("File extension not found for", file);
    return "not-supported";
  }

  switch (extension) {
    case "csv":
      return "csv";
    case "tsv":
      return "tsv";
    case "txt":
      return "txt";
    case "parquet":
      return "parquet";
    case "jpg":
      return "jpg";
    case "png":
      return "png";
    default:
      return "not-supported";
  }
}

export function getFileName(file: TGetFileTypeFile): string {
  if (file instanceof File) {
    return file.name;
  }

  return file.split("/").pop() || "No Filename";
}
