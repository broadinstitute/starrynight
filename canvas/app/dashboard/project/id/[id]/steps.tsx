"use client";
import React from "react";
import { Sidebar } from "@/components/custom/sidebar";
import { TProjectStep } from "@/services/step";
import { ProjectStepJobs } from "./jobs";
import { Button } from "@/components/ui/button";
import { Loader2 } from "lucide-react";

export type TStepsProps = {
  steps: TProjectStep[];
  projectDescription: string;
};

export function Steps(props: TStepsProps) {
  const { steps, projectDescription } = props;
  const [activeStep, setActiveStep] = React.useState(steps[0]);
  const [isExecuting, setIsExecuting] = React.useState(false);

  if (steps.length === 0) {
    return (
      <div className="flex flex-1 justify-center items-center p-4">
        <p>This project has no steps.</p>
      </div>
    );
  }

  return (
    <div className="flex flex-1 flex-col">
      <div className="py-4">
        <p>{projectDescription}</p>
        <br />
        <p>
          This project consists of {steps.length} step(s). You can either
          execute the steps individually, run individual jobs one by one, or use
          the &quot;Execute Project&quot; button to run all the steps and jobs
          at once.
        </p>
        <br />
        <Button size="sm" disabled={isExecuting}>
          {isExecuting && <Loader2 className="animate-spin mr-2" />}
          Execute Project
        </Button>
      </div>
      <div className="flex flex-col py-4 gap-4 flex-1 md:flex-row md:overflow-auto">
        <Sidebar
          active={activeStep.id}
          items={steps.map((step) => ({
            title: step.name,
            id: step.id,
            onClick: () => setActiveStep(step),
          }))}
        />
        <ProjectStepJobs step={activeStep} />
      </div>
    </div>
  );
}
