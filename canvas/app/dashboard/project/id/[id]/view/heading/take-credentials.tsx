import { Modal } from "@/components/custom/modal";
import { Button } from "@/components/ui/button";
import { useProjectStore } from "@/stores/project";
import { KeyRound, Settings } from "lucide-react";
import React from "react";
import { TakeCredentialsForm } from "./take-credentials-form";
import { ActionButton } from "@/components/custom/action-button";

const formId = "add-aws-credentials-form";

export function TakeCredentials() {
  const { project } = useProjectStore((state) => ({ project: state.project }));
  const [isOpen, setIsOpen] = React.useState(false);

  return (
    <Modal
      open={isOpen}
      onOpenChange={(state) => setIsOpen(state)}
      title="Add AWS Credentials"
      headerIcon={<Settings />}
      trigger={
        <ActionButton
          message="Add or update AWS Credentials"
          variant="outline"
          size="default"
          icon={<KeyRound />}
        >
          Credentials
        </ActionButton>
      }
      actions={[
        <Button key="add-creds" form={formId}>
          Add
        </Button>,
      ]}
      hasCloseButtonInFooter
    >
      <TakeCredentialsForm
        onRequestClose={() => setIsOpen(false)}
        projectId={project.id}
        formId={formId}
      />
    </Modal>
  );
}
