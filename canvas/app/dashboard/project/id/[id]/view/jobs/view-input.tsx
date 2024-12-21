import { ButtonWithTooltip } from "@/components/custom/button-with-tooltip";
import { Eye } from "lucide-react";

export function ViewJobInput() {
  // TODO: Implement View job input.
  return (
    <ButtonWithTooltip
      variant="ghost"
      size="icon"
      message="View input file"
      onClick={() => console.log("Not Implemented!")}
    >
      <Eye className="h-2 w-2" />
    </ButtonWithTooltip>
  );
}
