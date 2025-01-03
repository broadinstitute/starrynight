import { FileDisplay } from "../file-display";

export type TFileViewerDetailsSectionProps = {
  file: File;
};

export function FileViewerDetailsSection(
  props: TFileViewerDetailsSectionProps
) {
  const { file } = props;
  return (
    <div className="border-l border-l-gray-200  flex-1 max-w-80">
      <FileDisplay file={file} />
    </div>
  );
}
