import { TJob } from "@/services/job";
import { TProject, TProjectStatus } from "@/services/projects";
import { TRun } from "@/services/run";
import { TStep } from "@/services/step";
import { createStore } from "zustand/vanilla";

export type TState = {
  project: TProject;
  projectStatus: TProjectStatus;
  currentStep?: TStep;
  jobs: Record<string, TJob>;
  jobStatus: Record<string, TRun["run_status"]>;
};

export type TActions = {
  updateProjectStatus: (status: TProjectStatus) => void;
  updateCurrentStep: (currentStep: TStep) => void;
  addJobs: (jobs: TJob[]) => void;
  updateJobStatus: (id: string | number, status: TRun["run_status"]) => void;
};
export type TProjectStore = TState & TActions;

export type TCreateProjectStoreOptions = {
  project: TProject;
};

function getProjectStatus(project: TProject): TProjectStatus {
  if (project.is_configured) {
    return "configured";
  } else {
    return "not-configured";
  }

  // TODO: Add more status once we have them in the BE.
}

export function createProjectStore(options: TCreateProjectStoreOptions) {
  const { project } = options;
  const projectStatus = getProjectStatus(project);

  return createStore<TProjectStore>()((set, get) => ({
    project,
    projectStatus,
    jobs: {},
    jobStatus: {},
    updateProjectStatus: (projectStatus) => set({ projectStatus }),
    updateCurrentStep: (currentStep) => set({ currentStep }),
    addJobs: (jobs) => {
      const _jobStatus = {} as Record<string, TJob>;

      for (const job of jobs) {
        _jobStatus[job.id] = job;
      }
    },

    updateJobStatus: (id, status) => {
      const _jobStatus = get().jobStatus;
      _jobStatus[id] = status;
      set({ jobStatus: { ..._jobStatus } });
    },
  }));
}
