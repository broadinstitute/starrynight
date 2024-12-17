import { Modal } from "@/components/custom/modal";
import { FileInput } from "lucide-react";
import React from "react";

export type TJobInputModalProps = {
  title: string;
  trigger: React.ReactNode;
};

export function JobInputModal(props: TJobInputModalProps) {
  const { title, trigger } = props;

  return (
    <Modal title={title} trigger={trigger} headerIcon={<FileInput />}>
      this is file input modal.
    </Modal>
  );
}
