import { ButtonWithTooltip } from "@/components/custom/button-with-tooltip";
import { Modal } from "@/components/custom/modal";
import { Button } from "@/components/ui/button";
import { useProjectStore } from "@/stores/project";
import { Settings } from "lucide-react";
import React from "react";
import { TakeCredentialsForm } from "./take-credentials-form";

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
        <ButtonWithTooltip
          message="Add or update AWS Credentials"
          variant="outline"
        >
          <Settings className="mr-2 h-4 w-4" />
          Credentials
        </ButtonWithTooltip>
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
