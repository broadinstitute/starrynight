import { TProjectStepJob } from "@/services/job";
import { TProject } from "@/services/projects";
import { TProjectStep } from "@/services/step";
import { createStore } from "zustand/vanilla";

export type TProjectState = {
  project: TProject;
  steps: TProjectStep[];
  currentStep: TProjectStep | null;
  currentActiveStepJobs: TProjectStepJob[];
};

export type TProjectStoreActions = {
  updateSteps: (steps: TProjectStep[]) => void;
  updateCurrentStep: (step: TProjectStep) => void;
  updateCurrentStepJobs: (jobs: TProjectStepJob[]) => void;
};
export type TProjectStore = TProjectState & TProjectStoreActions;

export type TCreateProjectStoreOptions = {
  project: TProject;
};

export function createProjectStore(options: TCreateProjectStoreOptions) {
  const { project } = options;

  return createStore<TProjectStore>()((set) => ({
    project,
    steps: [],
    currentStep: null,
    currentActiveStepJobs: [],
    updateSteps: (steps) => set({ steps }),
    updateCurrentStep: (step) => set({ currentStep: step }),
    updateCurrentStepJobs: (jobs) => set({ currentActiveStepJobs: jobs }),
  }));
}
