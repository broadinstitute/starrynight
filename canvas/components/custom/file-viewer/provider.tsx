import React, {
  type ReactNode,
  createContext,
  useRef,
  useContext,
} from "react";
import { useStore } from "zustand";

import {
  TCreateFileViewerStoreOptions,
  type TFileViewerStore,
  createFileViewerStore,
} from "./store";

export type TFileViewerStoreApi = ReturnType<typeof createFileViewerStore>;

export const FileViewerStoreContext = createContext<
  TFileViewerStoreApi | undefined
>(undefined);

export type TFileViewerStoreProviderProps = {
  children: ReactNode;
  options: TCreateFileViewerStoreOptions;
};

export function FileViewerStoreProvider(props: TFileViewerStoreProviderProps) {
  const { children, options } = props;

  const storeRef = useRef<TFileViewerStoreApi>();

  if (!storeRef.current) {
    storeRef.current = createFileViewerStore(options);
  }

  return (
    <FileViewerStoreContext.Provider value={storeRef.current}>
      {children}
    </FileViewerStoreContext.Provider>
  );
}

export const useFileViewerStore = <T,>(
  selector: (store: TFileViewerStore) => T
): T => {
  const context = useContext(FileViewerStoreContext);

  if (!context) {
    throw new Error(
      `useFileViewerStore must be used within FileViewerStoreProvider`
    );
  }

  return useStore(context, selector);
};
