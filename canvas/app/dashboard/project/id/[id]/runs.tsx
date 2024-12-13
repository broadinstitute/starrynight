"use client";

import {
  TProjectStepJob,
  TProjectStepJobInput,
  updateJob,
} from "@/services/job";
import { TProjectStepJobRun } from "@/services/run";
import React from "react";
import { ProjectStepJobRun } from "./run";
import { RunsActions } from "./runs-actions";
import { ViewInputModal } from "./view-input-modal";
import { Label } from "@radix-ui/react-label";
import { Input } from "@/components/ui/input";
import { useProjectStore } from "@/stores/project";
import { mutate } from "swr";
import { FileViewer } from "@/components/custom/file-viewer";
import { toast } from "@/components/ui/use-toast";

export type TProjectStepJobRunProps = {
  runs: TProjectStepJobRun[];
  job: TProjectStepJob;
  mutateKey: string;
};

export function ProjectStepJobRuns(props: TProjectStepJobRunProps) {
  const { runs, job, mutateKey } = props;
  const { project } = useProjectStore((state) => ({
    project: state.project,
  }));

  function mutateFetchJob() {
    mutate(mutateKey, true);
    mutate(`/job/?step_id=${job.step_id}`, true);
  }

  async function updateAndSubmitJob(
    inputs: Record<string, TProjectStepJobInput>
  ) {
    const response = await updateJob({
      job: {
        ...job,
        inputs,
      },
    });

    if (response.ok) {
      mutateFetchJob();
    } else {
      toast({
        title: "Failed to save inputs.",
      });
    }
  }

  const inputs = React.useMemo(() => {
    const _inputs = Object.entries(job.inputs);
    return _inputs.map((input) => ({
      id: input[0],
      label: input[0],
      type: input[1].type,
      value: `${project.dataset_uri.replace(/\/$/, "")}/${
        input[1].value.replace(project.dataset_uri, "").replace(/^\//, "") || ""
      }`,
    }));
  }, [job.inputs, project.dataset_uri]);

  return (
    <div>
      <div className="border border-gray-200 rounded-md">
        <div className="flex items-center justify-between border-b border-b-gray-200 px-4 py-2">
          <div className="flex-1 font-bold">Inputs</div>
          <ViewInputModal
            inputs={inputs}
            title={`Inputs - ${job.name}`}
            isEditable={true}
            buttonTitle="Edit job inputs"
            primaryAction={{
              label: "Save",
              onClick: updateAndSubmitJob,
            }}
            emptyInputPlaceholder="Add input"
          />
          <div className="ml-4">
            <RunsActions runs={runs} job={job} mutateKey={mutateKey} />
          </div>
        </div>

        {inputs.map((input, index) => (
          <div
            key={input.label + index}
            className="flex items-center space-x-2 p-4"
          >
            <Label htmlFor={input.label + index}>{input.label}</Label>
            <Input
              value={input.value}
              id={input.label + index}
              disabled={true}
            />
            <FileViewer fileName={input.value} />
          </div>
        ))}
      </div>

      <h4 className="font-bold my-4">Runs</h4>
      {runs.map((run) => (
        <ProjectStepJobRun key={run.id} run={run} />
      ))}
      {runs.length === 0 && <p className="mb-4">No job is running.</p>}
    </div>
  );
}
