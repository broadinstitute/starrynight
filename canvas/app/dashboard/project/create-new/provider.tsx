import React from "react";
import {
  createCreateNewProjectStore,
  CreateNewProjectStoreContext,
  TCreateNewProjectStore,
} from "./store";

export type TCreateNewProjectProviderProps = React.PropsWithChildren<{}>;

export function CreateNewProjectProvider(
  props: TCreateNewProjectProviderProps
) {
  const { children } = props;

  const store = React.useRef<TCreateNewProjectStore>();

  if (!store.current) {
    store.current = createCreateNewProjectStore();
  }

  return (
    <CreateNewProjectStoreContext.Provider value={store.current}>
      {children}
    </CreateNewProjectStoreContext.Provider>
  );
}

export function withCreateNewProjectProvider(Comp: React.ComponentType) {
  return function WrappedComponent() {
    return (
      <CreateNewProjectProvider>
        <Comp />
      </CreateNewProjectProvider>
    );
  };
}
