import { ActionButton } from "@/components/custom/action-button";
import { useToast } from "@/components/ui/use-toast";
import { TRun, useKillRun } from "@/services/run";
import { XOctagon } from "lucide-react";
import { useCallback } from "react";

export type TKillRunProps = {
  run: TRun;
};

export function KillRun(props: TKillRunProps) {
  const { run } = props;
  const { toast } = useToast();

  const onError = useCallback(() => {
    toast({
      variant: "destructive",
      title: `Unable to kill ${run.name}.`,
    });
  }, [toast, run]);

  const onSuccess = useCallback(() => {
    toast({
      variant: "default",
      title: `${run.name} has been killed`,
    });
  }, [run, toast]);

  const { mutate: killRun, isPending } = useKillRun({
    onError,
    onSuccess,
  });

  const handleKillRun = useCallback(() => {
    killRun({ run_id: run.id });
  }, [run, killRun]);

  if (run.run_status !== "running") {
    /**
     * We can only kill a run if it is running or pending.
     */
    return null;
  }

  return (
    <ActionButton
      onClick={handleKillRun}
      variant="ghost-destructive"
      icon={<XOctagon />}
      isLoading={isPending}
      message="Kill this run"
    />
  );
}
