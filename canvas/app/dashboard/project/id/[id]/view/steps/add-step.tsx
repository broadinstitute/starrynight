import { Button } from "@/components/ui/button";
import { PlusIcon } from "lucide-react";
import React from "react";

export function ProjectSidebarAddStep() {
  const handleOnClick = React.useCallback((event: React.MouseEvent) => {
    event.preventDefault();
    event.stopPropagation();

    console.log("Adding a new step");
  }, []);

  return (
    <Button
      onClick={handleOnClick}
      variant="ghost"
      size="icon"
      className="hover:bg-slate-200"
    >
      <PlusIcon />
    </Button>
  );
}
