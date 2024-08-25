"use client";

import { Button } from "@/components/ui/button";
import { TProjectStepJobRun } from "@/services/run";
import { Loader2 } from "lucide-react";
import React from "react";
import { JobBadge } from "./badge";
import { FileViewer } from "@/components/custom/file-viewer";

export type TProjectStepJobRunProps = {
  run: TProjectStepJobRun;
};

export function ProjectStepJobRun(props: TProjectStepJobRunProps) {
  const { run } = props;

  return (
    <div className="space-y-4">
      <div>Name: {run.name}</div>
      <div>
        Status: <JobBadge status={run.run_status} />
      </div>
      {run.run_status === "success" && (
        <div>
          <FileViewer fileName="s3_file_url.test" />
        </div>
      )}
    </div>
  );
}
