import {
  CircleDotDashed,
  Loader2,
  PlayIcon,
  RotateCw,
  XIcon,
} from "lucide-react";
import { Button } from "../ui/button";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { TRunStatus } from "@/services/run";

export type TActionsButtonProps = {
  isDisabled?: boolean;
  onClick?: () => void;
  tooltipText?: string;
};

export type TActionsButtonsProps = {
  playButton: TActionsButtonProps;
  pendingButton: TActionsButtonProps;
  runningButton: TActionsButtonProps;
  failedButton: TActionsButtonProps;
  cancelButton: TActionsButtonProps;
  currentState: TRunStatus;
};

export function ActionsButtons(props: TActionsButtonsProps) {
  const {
    currentState,
    pendingButton,
    playButton,
    runningButton,
    failedButton,
    cancelButton,
  } = props;

  function getPrimaryAction() {
    switch (currentState) {
      case "init":
      case "success":
        return {
          icon: <PlayIcon className="h-4 w-4" />,
          ...playButton,
        };
      case "pending":
        return {
          icon: <CircleDotDashed className="h-4 w-4 animate-spin" />,
          ...pendingButton,
        };

      case "running":
        return {
          icon: <Loader2 className="h-4 w-4 animate-spin" />,
          ...runningButton,
        };

      case "failed":
        return {
          icon: <RotateCw className="h-4 w-4" />,
          ...failedButton,
        };
      default:
        return null;
    }
  }

  const action = getPrimaryAction();

  if (!action) {
    return null;
  }

  return (
    <div className="w-[85px]">
      <Tooltip>
        <TooltipTrigger asChild>
          <Button
            variant="ghost"
            size="icon"
            onClick={action.onClick}
            disabled={action.isDisabled}
            className={action.isDisabled ? "bg-gray-100 mr-2" : "mr-2"}
          >
            {action.icon}
          </Button>
        </TooltipTrigger>
        {action.tooltipText && (
          <TooltipContent className="bg-gray-50 text-black">
            <p>{action.tooltipText}</p>
          </TooltipContent>
        )}
      </Tooltip>
      <Tooltip>
        <TooltipTrigger asChild>
          <Button
            variant="ghost"
            size="icon"
            onClick={cancelButton.onClick}
            disabled={cancelButton.isDisabled}
            className={
              cancelButton.isDisabled ? "bg-gray-100" : "hover:bg-red-50"
            }
          >
            <XIcon className="h-4 w-4 text-destructive" />
          </Button>
        </TooltipTrigger>
        {cancelButton.tooltipText && (
          <TooltipContent className="bg-gray-50 text-black">
            <p>{cancelButton.tooltipText}</p>
          </TooltipContent>
        )}
      </Tooltip>
    </div>
  );
}
