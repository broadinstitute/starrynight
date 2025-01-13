import { useFileViewerStore } from "./provider";
import { FileDisplay } from "../file-display";

export function FileViewerDetailsSection() {
  const { filename, details, buffer, filetype } = useFileViewerStore(
    (store) => ({
      filename: store.name,
      details: store.details,
      buffer: store.bufferViewerOption,
      filetype: store.fileType,
    })
  );

  if (filetype === "notebook" || filetype === "not-supported") {
    return null;
  }

  return (
    <div className="border-l border-l-gray-200 pt-4 max-w-80 flex-1 pl-6">
      {buffer?.data && (
        <FileDisplay
          hasViewFileAction={false}
          file={new File([buffer.data], filename, { type: filetype })}
        />
      )}

      <table className="mt-4 text-sm">
        <thead>
          <tr>
            <th></th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {details.map(([label, value]) => (
            <tr key={label}>
              <td className="font-bold pr-2">{label}</td>
              <td>{value}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
