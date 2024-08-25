"use client";
import React from "react";
import { Sidebar } from "@/components/custom/sidebar";
import { ProjectStepJobs } from "./jobs";
import { useProjectStore } from "@/stores/project";

export function Steps() {
  const { steps, currentStep, updateCurrentStep } = useProjectStore(
    (state) => ({
      steps: state.steps,
      currentStep: state.currentStep,
      updateCurrentStep: state.updateCurrentStep,
    })
  );

  if (steps.length === 0) {
    return (
      <div className="flex flex-1 justify-center items-center p-4">
        <p>No steps to show! Add some steps to your pipeline.</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col py-4 gap-4 flex-1 md:flex-row md:overflow-auto">
      <Sidebar
        active={currentStep ? currentStep.id : ""}
        items={steps.map((step) => ({
          title: step.name,
          id: step.id,
          onClick: () => updateCurrentStep(step),
        }))}
      />
      {currentStep && <ProjectStepJobs />}
    </div>
  );
}
