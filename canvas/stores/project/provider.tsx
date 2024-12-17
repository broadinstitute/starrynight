import { type ReactNode, createContext, useRef, useContext } from "react";
import { useStore } from "zustand";

import { type TProjectStore, createProjectStore } from "./store";
import { TProject } from "@/services/projects";

export type TProjectStoreApi = ReturnType<typeof createProjectStore>;

export const ProjectStoreContext = createContext<TProjectStoreApi | undefined>(
  undefined
);

export type TProjectStoreProviderProps = {
  children: ReactNode;
  project: TProject;
};

export function ProjectStoreProvider(props: TProjectStoreProviderProps) {
  const { children, project } = props;

  const storeRef = useRef<TProjectStoreApi>();
  if (!storeRef.current) {
    storeRef.current = createProjectStore({
      project,
    });
  }

  return (
    <ProjectStoreContext.Provider value={storeRef.current}>
      {children}
    </ProjectStoreContext.Provider>
  );
}

export const useProjectStore = <T,>(
  selector: (store: TProjectStore) => T
): T => {
  const projectStoreContext = useContext(ProjectStoreContext);

  if (!projectStoreContext) {
    throw new Error(`useProjectStore must be used within ProjectStoreProvider`);
  }

  return useStore(projectStoreContext, selector);
};
