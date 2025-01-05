import { TFileType } from "@/utils/file";
import { createStore } from "zustand/vanilla";

export type TFileViewerStoreState = {
  buffer: ArrayBuffer;
  fileType: TFileType;
  name: string;
  details: [string, string | number][];
};

export type TFileViewerStoreActions = {
  addDetails: (details: [string, string | number][]) => void;
};

export type TFileViewerStore = TFileViewerStoreState & TFileViewerStoreActions;

export type TCreateFileViewerStoreOptions = {
  buffer: ArrayBuffer;
  fileType: TFileType;
  name: string;
};

export function createFileViewerStore(options: TCreateFileViewerStoreOptions) {
  const { buffer, fileType, name } = options;

  return createStore<TFileViewerStore>((set) => ({
    buffer,
    fileType,
    name,
    details: [],
    addDetails: (details) => {
      set({ details });
    },
  }));
}
