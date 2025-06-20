import { ActionButton } from "@/components/custom/action-button";
import { LogViewer } from "@/components/custom/log-viewer";
import { Modal } from "@/components/custom/modal";
import { TRun } from "@/services/run";
import { ScrollText } from "lucide-react";
import React from "react";

export type TRunViewLogProps = {
  run: TRun;
};

export function RunViewLog(props: TRunViewLogProps) {
  const { run } = props;

  return (
    <Modal
      title="Logs"
      trigger={<ActionButton icon={<ScrollText />} message="View logs" />}
      contentProps={{
        className:
          "sm:max-w-[95vw] md:max-w-[95vw] xl:max-w-[1250px] h-[95vh] max-h-[800px] flex flex-col gap-0",
      }}
      headerProps={{
        className: "border-b-transparent",
      }}
      footerProps={{
        className: "border-t-transparent",
      }}
    >
      <LogViewer endpoint={`ws://100.103.131.84:8000/ws/run/log/${run.id}`} />
    </Modal>
  );
}
