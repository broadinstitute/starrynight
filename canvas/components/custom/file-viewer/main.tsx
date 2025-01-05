import { FileViewerDetailsSection } from "./details-section";
import { FileViewerViewerSection } from "./viewer-section";

export function FileViewerMain() {
  return (
    <div className="flex flex-1">
      <FileViewerViewerSection />
      <FileViewerDetailsSection />
    </div>
  );
}
