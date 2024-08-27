"use client";

import { WS_BASE_URL } from "@/services/api";
import { TProjectStepJobRun } from "@/services/run";
import React from "react";
import { JobBadge } from "./badge";
import { FileViewer } from "@/components/custom/file-viewer";
import { ViewInput } from "./view-input";
import {
  Table,
  TableBody,
  TableCaption,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { LogViewer } from "@/components/custom/log-viewer";
import { downloadFile } from "@/utils/download";
import { getFile } from "@/services/s3";
import { useProjectStore } from "@/stores/project";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@radix-ui/react-accordion";

export type TProjectStepJobRunProps = {
  run: TProjectStepJobRun;
};

export function ProjectStepJobRun(props: TProjectStepJobRunProps) {
  const { run } = props;
  const { project } = useProjectStore((state) => ({ project: state.project }));

  async function handleDownload(url: string) {
    let response = await getFile(url, {
      projectId: project.id,
      toString: {},
    });

    if (!response) {
      alert("Failed to download file");
      return;
    }

    downloadFile({
      content: response,
      filename: url.split("/").pop()!,
    });
  }

  return (
    <div className="space-y-4 pt-4 rounded-md border border-gray-300 p-4 my-4 ">
      <Accordion type="single" collapsible>
        <AccordionItem value={`run-${run.id}`}>
          <AccordionTrigger>
            <div className="flex flex-1 items-center space-x-4">
              <div className="flex-1">{run.name}</div>
              <JobBadge status={run.run_status} />
              <ViewInput
                viewButtonTitle="View input"
                inputsRecord={run.inputs}
                isEditable={false}
                title={`Inputs - ${run.name}`}
                emptyInputPlaceholder="No input was provided."
              />
            </div>
          </AccordionTrigger>
          <AccordionContent>
            <div className="h-60 pt-4">
              <LogViewer endpoint={`${WS_BASE_URL}/ws/run/log/${run.id}`} />
            </div>
          </AccordionContent>
        </AccordionItem>
      </Accordion>
      {run.run_status === "success" && (
        <Table>
          <TableCaption>Job Output</TableCaption>
          <TableHeader>
            <TableRow>
              <TableHead>Name</TableHead>
              <TableHead>Type</TableHead>
              <TableHead>URI</TableHead>
              <TableHead className="w-[200px] pl-6">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {Object.entries(run.outputs).map(([name, data]) => (
              <TableRow key={name}>
                <TableCell className="font-medium">{name}</TableCell>
                <TableCell>{data.type}</TableCell>
                <TableCell>{data.uri}</TableCell>
                <TableCell>
                  <div className="space-x-2 flex items-center">
                    <FileViewer fileName={data.uri} />
                    <Button
                      onClick={() => handleDownload(data.uri)}
                      size="sm"
                      variant="outline"
                    >
                      Download
                    </Button>
                  </div>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      )}
    </div>
  );
}
