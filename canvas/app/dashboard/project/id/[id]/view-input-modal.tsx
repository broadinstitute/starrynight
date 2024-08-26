import { Button } from "@/components/ui/button";
import {
  DialogHeader,
  Dialog,
  DialogContent,
  DialogTitle,
  DialogTrigger,
  DialogFooter,
  DialogClose,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { toast } from "@/components/ui/use-toast";
import { TProjectStepJobInput } from "@/services/job";
import { uploadToS3 } from "@/services/s3";
import { useProjectStore } from "@/stores/project";
import { useRef, useState } from "react";

export type TViewInputModalProps = {
  title: string;
  buttonTitle: string;
  inputs: { id: string; label: string; value: string; type: string }[];
  isEditable: boolean;
  emptyInputPlaceholder?: string;
  primaryAction?: {
    label: string;
    onClick: (value: Record<string, TProjectStepJobInput>) => void;
  };
};

export function ViewInputModal(props: TViewInputModalProps) {
  const {
    title,
    inputs,
    buttonTitle,
    primaryAction,
    isEditable = false,
    emptyInputPlaceholder,
  } = props;
  const newValuesRefs = inputs.map(() => useRef<HTMLInputElement>(null));
  const inputRef = useRef<HTMLInputElement>(null);
  const { project } = useProjectStore((state) => ({ project: state.project }));
  const [isUploading, setIsUploading] = useState(false);

  async function uploadFile(url: string) {
    const fileInput = inputRef.current;
    if (!fileInput) return;

    const file = fileInput.files?.[0];
    if (!file) {
      return;
    }

    setIsUploading(true);
    const res = await uploadToS3(url, {
      ContentType: file.type,
      Body: file,
      projectId: project.id,
    });

    if (!res) {
      toast({
        title: "Failed to upload file.",
        variant: "destructive",
      });
    } else {
      toast({
        title: "File uploaded successfully.",
      });
    }

    setIsUploading(false);
  }

  function handlePrimaryAction() {
    const values = inputs.reduce(
      (acc, input, index) => ({
        ...acc,
        [input.id]: {
          type: input.type,
          value: newValuesRefs[index].current?.value || "",
        },
      }),
      {} as Record<string, TProjectStepJobInput>
    );

    primaryAction?.onClick(values);
  }

  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button variant="outline" size="sm">
          {buttonTitle}
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>
            {title.length > 35 ? `${title.substring(0, 35)}...` : title}
          </DialogTitle>
        </DialogHeader>
        {inputs.map((input, index) => (
          <div key={input.label + index} className="space-y-2">
            <Label htmlFor={input.label + index}>{input.label}</Label>
            <Input
              defaultValue={input.value}
              ref={newValuesRefs[index]}
              id={input.label + index}
              disabled={!isEditable}
              placeholder={emptyInputPlaceholder}
            />
            {isEditable && <small>Full path required</small>}
            {isEditable && (
              <div className="flex space-x-2">
                <Input type="file" ref={inputRef} />
                <Button
                  onClick={() =>
                    uploadFile(newValuesRefs[index].current?.value || "")
                  }
                  disabled={isUploading}
                >
                  Upload
                </Button>
              </div>
            )}
          </div>
        ))}
        <DialogFooter className="sm:justify-start md:justify-between">
          <DialogClose asChild>
            <Button type="button" className="my-1" variant="secondary">
              Close
            </Button>
          </DialogClose>
          {primaryAction && (
            <DialogClose asChild>
              <Button
                className="my-1"
                type="submit"
                onClick={handlePrimaryAction}
              >
                {primaryAction.label}
              </Button>
            </DialogClose>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
