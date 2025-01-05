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

  return file.split("/").pop() || "No Filename";
}
