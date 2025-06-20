import React, { useMemo } from "react";
import { ActionButton } from "@/components/custom/action-button";
import { Check, Upload, XIcon } from "lucide-react";
import { ProjectJobInputEditWarningModal } from "./job-input-edit-warning-modal";
import { PathFieldWithAction } from "@/components/custom/path-filed-with-actions";
import { useToast } from "@/components/ui/use-toast";
import {
  GET_JOBS_QUERY_KEY,
  getJobs,
  TJob,
  useUpdateJob,
} from "@/services/job";
import { FeatureNotImplementedModal } from "@/components/custom/feature-not-implemented-modal";
import { useQueryClient } from "@tanstack/react-query";
import { useProjectStore } from "@/stores/project";
import { TSpecPathRecord } from "@/services/misc";
import { JobInputUploadFile } from "./job-input-upload-file";
import { useUploadFile } from "@/services/s3";

export type TProjectJobInputProps = {
  job: TJob;
  inputPath: string;
  inputName: string;
  onInputPathChange: (value: string) => void;
  onRequestView: () => void;
};

export function ProjectJobInputEdit(props: TProjectJobInputProps) {
  const { onRequestView, inputName, inputPath, job, onInputPathChange } = props;
  const [isWarningModalOpen, setIsWarningModalOpen] = React.useState(false);
  const oldValue = React.useRef(inputPath);
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const { projectID } = useProjectStore((store) => ({
    projectID: store.project.id,
  }));

  // To upload new file.
  const [inputFile, setInputFile] = React.useState<File | null>(null);

  const [isUpdating, setIsUpdating] = React.useState(false);

  const handleOnSuccessfulSavingChanges = React.useCallback(async () => {
    await queryClient.invalidateQueries({
      queryKey: [GET_JOBS_QUERY_KEY, projectID],
    });

    /**
     * After invalidating fetching new data to
     * make sure the UI has the latest data.
     */
    await queryClient.prefetchQuery({
      queryKey: [GET_JOBS_QUERY_KEY, projectID],
      queryFn: () => getJobs({ project_id: projectID }),
    });

    onRequestView();
  }, [queryClient, projectID, onRequestView]);

  const handleOnErrorSavingChanges = React.useCallback(() => {
    toast({
      title: "Unable to save changes. Please try again later.",
      variant: "destructive",
    });
  }, [toast]);

  const { isPending, mutate: updateJob } = useUpdateJob({
    onError: handleOnErrorSavingChanges,
    onSuccess: handleOnSuccessfulSavingChanges,
  });

  const { mutateAsync: uploadFile } = useUploadFile({});

  const hasAnyFieldUpdated = useMemo(() => {
    if (inputFile) {
      // If input file is not null, meaning we have updated input file.
      return true;
    }

    if (oldValue.current !== inputPath) {
      // Input has been changed.
      return true;
    }
  }, [inputFile, inputPath]);

  const handleOnCloseEditingModeClick = React.useCallback(() => {
    if (hasAnyFieldUpdated) {
      setIsWarningModalOpen(true);
      return;
    }

    onRequestView();
  }, [hasAnyFieldUpdated, onRequestView]);

  const handleOnWarningModalPrimaryActionClick = React.useCallback(() => {
    setInputFile(null);
    onInputPathChange(oldValue.current);
    onRequestView();
  }, [onInputPathChange, onRequestView]);

  const handleOnSaveChanges = React.useCallback(async () => {
    if (!hasAnyFieldUpdated) {
      // if no filed has been updated, then we don't have any thing to
      // updated, hence closing the edit view.
      onRequestView();
    }

    setIsUpdating(true);
    if (inputFile) {
      try {
        const formdata = new FormData();
        formdata.append("file", inputFile);

        await uploadFile({
          filepath: inputPath,
          formdata,
        });
      } catch {
        toast({
          title: "Uable to upload file. Please try again.",
          variant: "destructive",
        });
        setIsUpdating(false);
        return;
      }
    }

    const specInputs: Record<string, TSpecPathRecord> = {};

    Object.entries(job.spec.inputs).forEach(([key, input]) => {
      if (input.name === inputName) {
        specInputs[key] = { ...input, value: inputPath };
      } else {
        specInputs[key] = input;
      }
    });

    updateJob({
      job: {
        ...job,
        spec: {
          ...job.spec,
          inputs: {
            ...job.spec.inputs,
            ...specInputs,
          },
        },
      },
    });
  }, [
    hasAnyFieldUpdated,
    inputFile,
    job,
    updateJob,
    onRequestView,
    uploadFile,
    inputPath,
    toast,
    inputName,
  ]);

  return (
    <>
      <PathFieldWithAction
        pathRecord={{
          id: inputPath,
          name: inputName,
          type: "path",
          value: inputPath,
        }}
        inputProps={{
          onChange: (e) => onInputPathChange(e.currentTarget.value),
          autoFocus: true,
          disabled: isUpdating,
        }}
        actions={[
          {
            id: "upload-file",
            children: (
              <JobInputUploadFile
                inputFile={inputFile}
                updateInputFile={setInputFile}
                disabled={isUpdating}
              />
            ),
          },
          {
            id: "close-editing-mode",
            children: (
              <ActionButton
                icon={<XIcon />}
                message="Close editing mode"
                variant="ghost-warning"
                onClick={handleOnCloseEditingModeClick}
                disabled={isUpdating}
              />
            ),
          },
          {
            id: "save-changes",
            children: (
              <ActionButton
                onClick={handleOnSaveChanges}
                isLoading={isUpdating}
                disabled={!hasAnyFieldUpdated}
                icon={<Check />}
                message="Save changes"
                key="save-changes"
              />
            ),
          },
        ]}
      />

      <ProjectJobInputEditWarningModal
        primaryActionCallback={handleOnWarningModalPrimaryActionClick}
        isOpen={isWarningModalOpen}
        onOpenChange={setIsWarningModalOpen}
      />
    </>
  );
}
