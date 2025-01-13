import React from "react";
import { VariableSizeGrid as Grid } from "react-window";
import { FileViewerTableViewCell } from "./cell";

export type TFileViewerTableView = {
  rows: string[][];
  header: string[];
  /**
   * Width and height of parent element.
   */
  parentDimension: [number, number];
};

export function FileViewerTableView(props: TFileViewerTableView) {
  const { rows, header, parentDimension } = props;
  const data = React.useMemo(() => [header, ...rows], [rows, header]);

  const getColumWidth = React.useCallback(
    (index: number) => {
      let maxSoFar = 100;

      for (let row = 0; row < 100 && row < rows.length; row++) {
        const val = data[row][index];
        let width = 100;
        if (typeof val === "string") {
          width = val.length * 8;
        }

        if (width > maxSoFar) {
          maxSoFar = width;
        }
      }

      return Math.min(maxSoFar, 300);
    },
    [rows.length, data]
  );

  const getRowHeight = React.useCallback(
    (index: number) => {
      let maxSoFar = 32;

      for (let col = 0; col < header.length; col++) {
        const val = data[index][col];
        let height = 32;

        if (typeof val === "string") {
          height = Math.round(val.length / 32) * 32;
        }
        if (height > maxSoFar) {
          maxSoFar = height;
        }
      }

      return Math.min(maxSoFar, 100);
    },
    [header.length, data]
  );

  return (
    <Grid
      columnWidth={getColumWidth}
      width={parentDimension[0]}
      height={parentDimension[1]}
      rowHeight={getRowHeight}
      columnCount={header.length}
      rowCount={rows.length + 1}
      className="bg-accent border-l-accent border-l overflow-auto"
      overscanRowCount={50}
    >
      {({ columnIndex, rowIndex, style }) => (
        <FileViewerTableViewCell
          data={data[rowIndex][columnIndex]}
          isHeader={rowIndex === 0}
          style={style}
        />
      )}
    </Grid>
  );
}
