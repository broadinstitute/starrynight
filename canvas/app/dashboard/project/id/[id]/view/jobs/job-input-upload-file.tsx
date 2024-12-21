import { ButtonWithTooltip } from "@/components/custom/button-with-tooltip";
import { FileDisplay } from "@/components/custom/file-display";
import { buttonVariants } from "@/components/ui/button";
import {
  HoverCardContent,
  HoverCard,
  HoverCardTrigger,
} from "@/components/ui/hover-card";
import { Input } from "@/components/ui/input";
import clsx from "clsx";
import { Check, Upload } from "lucide-react";
import React from "react";

export type TJobInputUploadFileProps = {
  inputFile?: File | null;
  updateInputFile: (file: File | null) => void;
  disabled?: boolean;
};

export function JobInputUploadFile(props: TJobInputUploadFileProps) {
  const { inputFile, updateInputFile, disabled } = props;

  const handleOnInputFileChange = React.useCallback(
    (event: React.FormEvent<HTMLInputElement>) => {
      if (event.currentTarget.files) {
        updateInputFile(event.currentTarget.files[0]);
      }
    },
    [updateInputFile]
  );

  const handleOnInputFileRemoved = React.useCallback(() => {
    updateInputFile(null);
  }, [updateInputFile]);

  return (
    <HoverCard>
      <HoverCardTrigger asChild>
        <label
          className={clsx(
            buttonVariants({ variant: "ghost", size: "icon" }),
            "cursor-pointer relative",
            disabled && "pointer-events-none text-gray-500"
          )}
        >
          <Input
            onChange={handleOnInputFileChange}
            type="file"
            className="hidden"
            disabled={!!inputFile || disabled}
          />
          <Upload />
          {inputFile && !disabled && (
            <span className="absolute top-1 right-1 inline-block w-1 h-1 bg-red-500 rounded-full"></span>
          )}
        </label>
      </HoverCardTrigger>
      <HoverCardContent className="w-96">
        {!inputFile ? (
          <div className="text-gray-400">
            No file selected. If you want to upload a new file then click on the
            upload icon (
            <Upload className="inline-flex h-4 w-4" />) to select a file to
            upload.
          </div>
        ) : (
          <div className="flex flex-col space-y-4">
            <p>
              The selected file will be uploaded only after you click the save
              button (<Check className="inline-flex h-4 w-4" />
              ).
            </p>
            <FileDisplay file={inputFile} />
            <ButtonWithTooltip
              variant="destructive"
              message="Remove the selected file."
              onClick={handleOnInputFileRemoved}
            >
              Remove
            </ButtonWithTooltip>
          </div>
        )}
      </HoverCardContent>
    </HoverCard>
  );
}
