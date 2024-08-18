"use client";
import React from "react";
import { Sidebar } from "@/components/custom/sidebar";
import { TProjectStep } from "@/services/step";
import { ProjectStepJobs } from "./jobs";

export type TStepsProps = {
  steps: TProjectStep[];
};

export function Steps(props: TStepsProps) {
  const { steps } = props;
  const [activeStep, setActiveStep] = React.useState(steps[0]);

  return (
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
  );
}
