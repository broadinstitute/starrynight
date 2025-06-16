import { ActionButton } from "@/components/custom/action-button";
import { Modal } from "@/components/custom/modal";
import { Settings } from "lucide-react";
import React from "react";
import { ProjectSettingsView } from "./view";

export function ProjectSettings() {
  const [isOpen, setIsOpen] = React.useState(false);

  const onRequestCloseModal = React.useCallback(() => {
    setIsOpen(false);
  }, []);

  return (
    <Modal
      open={isOpen}
      contentProps={{
        className:
          "sm:max-w-[95vw] md:max-w-5xl h-[95vh] max-h-[800px] flex flex-col gap-0",
      }}
      footerProps={{
        className: "hidden",
      }}
      onOpenChange={(state) => setIsOpen(state)}
      title="Project Settings"
      headerIcon={<Settings />}
      trigger={
        <ActionButton
          message="Configure project wide settings, like adding aws credentials etc."
          variant="outline"
          size="default"
          icon={<Settings />}
        >
          Project Settings
        </ActionButton>
      }
    >
      <ProjectSettingsView onRequestClose={onRequestCloseModal} />
    </Modal>
  );
}
