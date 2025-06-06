export type TDownloadFileOptions = {
  content: string | Uint8Array | Blob | ArrayBuffer;
  filename: string;
};

export function downloadFile(options: TDownloadFileOptions) {
  const { content, filename } = options;
  let type = "application/";

  if (filename.endsWith(".txt") || filename.endsWith(".cppipe")) {
    type += "txt";
  } else if (filename.endsWith(".xlsx")) {
    type += "xlsx";
  } else if (filename.endsWith(".csv")) {
    type += "csv";
  } else if (filename.endsWith(".tsv")) {
    type += "tsv";
  } else if (filename.endsWith(".png")) {
    type = "image/png";
  } else if (filename.endsWith(".parquet")) {
    type += "parquet";
  }

  const blob = new Blob([content], { type });
  const link = document.createElement("a");
  link.href = window.URL.createObjectURL(blob);
  link.download = filename;
  link.click();
}
