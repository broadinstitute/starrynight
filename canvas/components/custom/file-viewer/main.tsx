import { FileViewerDetailsSection } from "./details-section";
import { FileViewerViewerSection } from "./viewer-section";

export type TFileViewerMainProps = {
  file: File;
};

export function FileViewerMain(props: TFileViewerMainProps) {
  const { file } = props;

  return (
    <div className="flex flex-1">
      <FileViewerViewerSection file={file} />
      <FileViewerDetailsSection file={file} />
    </div>
  );
}
