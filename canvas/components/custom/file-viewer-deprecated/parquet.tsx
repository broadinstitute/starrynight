import React from "react";
import { parquetRead, parquetMetadata, parquetSchema } from "hyparquet";
import { AutoSizer, Grid } from "react-virtualized";

export type TParquetFileViewProps = {
  data: Blob;
};
export function ParquetFileViewer(props: TParquetFileViewProps) {
  const [isProcessing, setIsProcessing] = React.useState(true);
  const [rows, setRows] = React.useState<string[][]>([]);
  const [headers, setHeaders] = React.useState<string[]>([]);

  const { data } = props;

  const processData = React.useCallback(async () => {
    setIsProcessing(true);
    const arrayBuffer = await data.arrayBuffer();
    const { children } = parquetSchema(parquetMetadata(arrayBuffer));
    const _header = children.map((child) => child.element.name);

    setHeaders(_header);

    await parquetRead({
      file: arrayBuffer,
      onComplete: (data: string[][]) => setRows([_header, ...data]),
    });
    setIsProcessing(false);
  }, [data]);

  React.useEffect(() => {
    processData();
  }, [processData]);

  if (isProcessing) {
    return <div>Processing..</div>;
  }
  return (
    <div className="h-[600px]">
      <AutoSizer>
        {({ width, height }) => (
          <Grid
            columnCount={headers.length}
            columnWidth={400}
            rowCount={rows.length}
            rowHeight={({ index }) => {
              const data = rows[index][0];
              const size = (data.length / 21) * 30;
              return size < 20 ? 20 : size;
            }}
            height={height}
            cellRenderer={({ rowIndex, columnIndex, key, style }) => {
              return (
                <div key={key} style={style}>
                  {rows[rowIndex][columnIndex]}
                </div>
              );
            }}
            width={width}
          />
        )}
      </AutoSizer>
    </div>
  );
}
