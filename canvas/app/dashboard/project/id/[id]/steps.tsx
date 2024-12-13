"use client";
import React from "react";
import { Sidebar } from "@/components/custom/sidebar";
import { ProjectStepJobs } from "./jobs";
import { useProjectStore } from "@/stores/project";
import { useUpdateSearchParams } from "@/hooks/useUpdateSearchParams";
import { TProjectStep } from "@/services/step";

export function Steps() {
  const { update } = useUpdateSearchParams();
  const { steps, currentStep, updateCurrentStep } = useProjectStore(
    (state) => ({
      steps: state.steps,
      currentStep: state.currentStep,
      updateCurrentStep: state.updateCurrentStep,
    })
  );

  function onSidebarClick(step: TProjectStep) {
    update({ step: String(step.id) });
    updateCurrentStep(step);
  }

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
          onClick: () => onSidebarClick(step),
        }))}
      />
      {currentStep && <ProjectStepJobs />}
    </div>
  );
}
