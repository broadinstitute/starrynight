import { TProject } from "@/services/projects";
import { TStep } from "@/services/step";
import { createStore } from "zustand/vanilla";

export type TState = {
  project: TProject;
  projectStatus: "running" | "idle";
  currentStep?: TStep;
};

export type TActions = {
  updateProjectStatus: (status: "running" | "idle") => void;
  updateCurrentStep: (currentStep: TStep) => void;
};
export type TProjectStore = TState & TActions;

export type TCreateProjectStoreOptions = {
  project: TProject;
};

export function createProjectStore(options: TCreateProjectStoreOptions) {
  const { project } = options;
  return createStore<TProjectStore>()((set) => ({
    project,
    projectStatus: "idle",
    updateProjectStatus: (projectStatus) => set({ projectStatus }),
    updateCurrentStep: (currentStep) => set({ currentStep }),
  }));
}
