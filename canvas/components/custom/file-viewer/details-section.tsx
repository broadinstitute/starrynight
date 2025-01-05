import { useFileViewerStore } from "./provider";
import { FileDisplay } from "../file-display";

export function FileViewerDetailsSection() {
  const { filename, details, buffer, filetype } = useFileViewerStore(
    (store) => ({
      filename: store.name,
      details: store.details,
      buffer: store.buffer,
      filetype: store.fileType,
    })
  );

  return (
    <div className="border-l border-l-gray-200 pt-4 max-w-80 flex-1 pl-6">
      <FileDisplay
        hasViewFileAction={false}
        file={new File([buffer], filename, { type: filetype })}
      />

      <table className="mt-4 text-sm">
        <thead>
          <th></th>
          <th></th>
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
