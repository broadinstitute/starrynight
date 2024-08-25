import { Button } from "@/components/ui/button";
import "react-datasheet-grid/dist/style.css";
import { DataSheetGrid, textColumn, keyColumn } from "react-datasheet-grid";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { DSVRowArray, csvParse, tsvParse } from "d3-dsv";
import { getFile } from "@/services/s3";
import { Eye, Loader2 } from "lucide-react";
import React from "react";
import Image from "next/image";
import { useProjectStore } from "@/stores/project";

interface DSVRendererProps {
  data: DSVRowArray;
}
const DSVRenderer = (props: DSVRendererProps) => {
  const { data } = props;
  const columns = data.columns.map((col) => {
    return { ...keyColumn(col, textColumn), title: col, disabled: true };
  });
  return (
    <div
      style={{
        maxWidth: "calc(100vw - 60px)",
      }}
    >
      <DataSheetGrid
        value={data}
        columns={columns}
        addRowsComponent={false}
        disableContextMenu
      />
    </div>
  );
};

interface FileViewerProps {
  fileName: string;
}

export function FileViewer(props: FileViewerProps) {
  const { project } = useProjectStore((state) => ({ project: state.project }));
  const { fileName } = props;
  const [viewContent, setViewContent] = React.useState("");
  const [isLoading, setIsLoading] = React.useState(true);

  async function fetchData() {
    if (fileName.endsWith(".xlsx")) {
      setViewContent("Please download to view this file.");
      setIsLoading(false);
      return;
    }
    const encoding = fileName.endsWith(".png") ? "base64" : "utf-8";
    const data = await getFile(fileName, {
      toString: { encoding },
      projectId: project.id,
    });

    if (data && typeof data === "string") {
      if (fileName.endsWith(".png")) {
        setViewContent(`data:image/png;base64,${data}`);
      } else {
        setViewContent(data);
      }
    } else {
      console.log("Failed to load file.", data);
    }

    setIsLoading(false);
  }

  const loading = isLoading;
  const failedToLoad = !isLoading && !viewContent;
  const loaded = !isLoading && viewContent;
  const isImage = fileName.endsWith(".png");
  const isCSV = fileName.endsWith(".csv");
  const isTSV = fileName.endsWith(".tsv");
  const isTXT = fileName.endsWith(".txt");
  const isExcel = fileName.endsWith(".xlsx");

  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button variant="ghost" onClick={fetchData}>
          <Eye className="mr-2 h-4 w-4" /> View
        </Button>
      </DialogTrigger>
      <DialogContent className="max-w-full w-full">
        <DialogHeader>
          <DialogTitle>{fileName.split("/").pop()}</DialogTitle>
        </DialogHeader>
        {loading && (
          <div className="p-4 flex justify-center items-center">
            <Loader2 className="mr-2 h-6 w-6 animate-spin" />
          </div>
        )}

        {failedToLoad && <div>Failed to load.</div>}
        {loaded && isExcel && <div>Please download to view the file!</div>}
        {loaded && isCSV && <DSVRenderer data={csvParse(viewContent)} />}
        {loaded && isTSV && <DSVRenderer data={tsvParse(viewContent)} />}
        {loaded && isTXT && <p> {viewContent} </p>}
        {loaded && isImage && (
          <div className="flex justify-center">
            <Image
              objectFit="contain"
              objectPosition="center"
              height={1600}
              width={1600}
              src={viewContent}
              alt={fileName}
            />
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}
