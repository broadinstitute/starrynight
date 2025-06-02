import { ActionButton } from "@/components/custom/action-button";
import { Modal } from "@/components/custom/modal";
import { Settings } from "lucide-react";
import React from "react";
import { ProjectSettingsView } from "./view";

export function ProjectSettings() {
  const [isOpen, setIsOpen] = React.useState(false);

  return (
    <Modal
      open={isOpen}
      contentProps={{
        className:
          "sm:max-w-[95vw] md:max-w-2xl h-[95vh] max-h-[800px] flex flex-col gap-0",
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
      <ProjectSettingsView />
    </Modal>
  );
}
