import { TFileType } from "@/utils/file";
import { createStore } from "zustand/vanilla";

export type TFileViewerStoreState = {
  name: string;
  details: [string, string | number][];
  fileType: TFileType;

  /**
   * If we have a file as a buffer, and want to
   * use our own viewer for it.
   */
  bufferViewerOption?: {
    data: ArrayBuffer;
  };

  /**
   * If we want to use an iframe for viewing the file.
   */
  iframeViewerOption?: {
    src: string;
  };

  /**
   * If we want to list all the files in the S3 directory.
   */
  s3DirectoryViewerOption?: {
    url: string;
  };
};

export type TFileViewerStoreActions = {
  addDetails: (details: [string, string | number][]) => void;
};

export type TFileViewerStore = TFileViewerStoreState & TFileViewerStoreActions;

export type TCreateFileViewerStoreOptions = {
  bufferViewerOption?: {
    data: ArrayBuffer;
  };
  iframeViewerOption?: {
    src: string;
  };
  s3DirectoryViewerOption?: {
    url: string;
  };
  fileType: TFileType;
  name: string;
};

export function createFileViewerStore(options: TCreateFileViewerStoreOptions) {
  const {
    bufferViewerOption,
    iframeViewerOption,
    s3DirectoryViewerOption,
    fileType,
    name,
  } = options;

  return createStore<TFileViewerStore>((set) => ({
    bufferViewerOption,
    iframeViewerOption,
    s3DirectoryViewerOption,
    fileType,
    name,
    details: [],
    addDetails: (details) => {
      set({ details });
    },
  }));
}
