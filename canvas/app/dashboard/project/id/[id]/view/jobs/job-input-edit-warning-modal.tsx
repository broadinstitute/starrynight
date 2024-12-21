import { Modal } from "@/components/custom/modal";
import { Button } from "@/components/ui/button";
import { TriangleAlert } from "lucide-react";

export type TProjectJobInputEditWarningModalProps = {
  isOpen: boolean;
  onOpenChange: (state: boolean) => void;
  primaryActionCallback: () => void;
};

export function ProjectJobInputEditWarningModal(
  props: TProjectJobInputEditWarningModalProps
) {
  const { isOpen, onOpenChange, primaryActionCallback } = props;

  return (
    <Modal
      title="Are you sure?"
      headerIcon={<TriangleAlert />}
      open={isOpen}
      onOpenChange={onOpenChange}
      trigger={<></>}
      hasCloseButtonInFooter
      actions={[
        <Button
          key="sure"
          onClick={primaryActionCallback}
          className="bg-yellow-600 hover:bg-yellow-500"
        >
          Sure
        </Button>,
      ]}
    >
      You have unsaved changes. Your changes will be lost.
    </Modal>
  );
}
