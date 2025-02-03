import React from "react";
import { createStore, useStore } from "zustand";

export type TCreateNewProjectState = {
  currentStep: number;
  isFormSubmitting: boolean;
};

export type TCreateNewProjectAction = {
  updateCurrentStep: (step: number) => void;
  updateIsFormSubmitting: (state: boolean) => void;
};

export type TCreateNewProjectStoreOptions = {};

export function createCreateNewProjectStore() {
  return createStore<TCreateNewProjectState & TCreateNewProjectAction>(
    (set) => ({
      currentStep: 0,
      isFormSubmitting: false,
      updateCurrentStep: (step) => set({ currentStep: step }),
      updateIsFormSubmitting: (state) => set({ isFormSubmitting: state }),
    })
  );
}

export type TCreateNewProjectStore = ReturnType<
  typeof createCreateNewProjectStore
>;

export const CreateNewProjectStoreContext =
  React.createContext<null | TCreateNewProjectStore>(null);

export function useCreateNewProjectStore<T>(
  selector: (store: TCreateNewProjectState & TCreateNewProjectAction) => T
) {
  const context = React.useContext(CreateNewProjectStoreContext);

  if (!context) {
    throw new Error(
      `useCreateProject must be used within CreateProjectStoreProvider.`
    );
  }

  return useStore(context, selector);
}
