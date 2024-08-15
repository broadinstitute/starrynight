"use client";

import { ColumnDef } from "@tanstack/react-table";
import { TFacets, THit } from "./types";
import {
  AccordionItem,
  AccordionTrigger,
} from "@/src/components/ui/accordion";
import { Button } from "@/src/components/ui/button";
import { Download, Eye, Loader2 } from "lucide-react";
import { get_key_file } from "../../lib/aws_s3";
import React from "react";
import { FileViewer } from "./file-viewer";

export const columns: ColumnDef<THit>[] = [
  {
    accessorKey: "value",
    header: "Key",
    cell: ({ row }) => <div>{row.getValue("value")}</div>,
  },
  {
    accessorKey: "count",
    header: "Hits",
    cell: ({ row }) => <div>{row.getValue("count")}</div>,
  },
  {
    accessorKey: "",
    header: "Actions",
    cell: ({ row }) => <ProjectKeyActions filename={row.getValue("value")} />,
  },
];

type TProjectKeyActions = {
  filename: string;
};

function ProjectKeyActions(props: TProjectKeyActions) {
  const { filename } = props;
  const [isDownloadLoading, setIsDownloadLoading] = React.useState(false);

  function downloadData(data: Uint8Array) {
    let type = "application/";

    if (filename.endsWith(".txt")) {
      type += "txt";
    } else if (filename.endsWith(".xlsx")) {
      type += "xlsx";
    } else if (filename.endsWith(".csv")) {
      type += "csv";
    } else if (filename.endsWith(".tsv")) {
      type += "tsv";
    } else if (filename.endsWith(".png")) {
      type = "image/png";
    }

    const blob = new Blob([data], { type });
    const link = document.createElement("a");
    link.href = window.URL.createObjectURL(blob);
    link.download = filename;
    link.click();
    setIsDownloadLoading(false);
  }

  async function fetchData() {
    const data = await get_key_file(filename);
    return data || "";
  }

  return (
    <div>
      <FileViewer fileName={filename} />
      <Button
        variant="ghost"
        disabled={isDownloadLoading}
        onClick={async () => {
          setIsDownloadLoading(true);
          const data = await fetchData();
          if (!data) {
            setIsDownloadLoading(false);
            return;
          }
          downloadData(data as Uint8Array);
        }}
      >
        {isDownloadLoading && (
          <>
            <Loader2 className="mr-2 h-4 w-4 animate-spin" /> Downloading...
          </>
        )}
        {!isDownloadLoading && (
          <>
            <Download className="mr-2 h-4 w-4" /> Download
          </>
        )}
      </Button>
    </div>
  );
}

export const facetColumns: ColumnDef<TFacets>[] = [
  {
    accessorKey: "value",
    header: "Project ID",
    cell: ({ row }) => <div>{row.getValue("value")}</div>,
  },
  {
    accessorKey: "count",
    header: "Hits",
    cell: ({ row }) => <div>{row.getValue("count")}</div>,
  },
  {
    header: "View",
    cell: ({ row }) => {
      return (
        <AccordionItem className="border-0 hover:no-underline" value={row.id}>
          <AccordionTrigger className="p-0 no-underline hover:no-underline">
          </AccordionTrigger>
        </AccordionItem>
      );
    },
  },
];
