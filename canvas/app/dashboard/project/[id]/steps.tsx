"use client";
import React from "react";
import { StepsMainArea } from "./steps-main-area";
import { Sidebar } from "@/components/custom/sidebar";

export type TStep = {
  title: string;
};

export type TStepsProps = {
  steps: TStep[];
};

export function Steps(props: TStepsProps) {
  const { steps } = props;
  const [activeStep, setActiveStep] = React.useState(steps[0]);

  return (
    <div className="flex flex-col py-4 gap-4 flex-1 md:flex-row md:overflow-auto">
      <Sidebar
        items={steps.map((step) => ({
          title: step.title,
          onClick: () => setActiveStep(step),
        }))}
      />
      <StepsMainArea content={activeStep} />
    </div>
  );
}
