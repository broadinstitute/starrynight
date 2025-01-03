import clsx from "clsx";
import React from "react";
import { WithTooltip } from "../../with-tooltip";
import { useToast } from "@/components/ui/use-toast";
import { Clipboard } from "lucide-react";

export type TFileViewerTableViewCellProps = {
  style: React.CSSProperties;
  text: string;
  isHeader: boolean;
};

export function FileViewerTableViewCell(props: TFileViewerTableViewCellProps) {
  const { style, text, isHeader } = props;
  const { toast } = useToast();

  const THRESHOLD = (+style.width! / 8) * (+style.height! / 32) - 3;
  const hasOverflow = text.length > THRESHOLD;

  const handleKeyboardDownEvent = React.useCallback(
    (event: React.KeyboardEvent) => {
      if ((event.ctrlKey || event.metaKey) && event.key === "c") {
        navigator.clipboard.writeText(text);
        toast({
          variant: "default",
          title: (
            <div className="flex space-x-1">
              <Clipboard /> <span>Copied!</span>
            </div>
          ),
        });
      }
    },
    [text]
  );

  return (
    <div
      style={style}
      className={clsx(
        "flex items-center justify-center w-full h-full px-2 py-1 border-t-transparent border-l-transparent border text-sm overflow-hidden text-ellipsis line-clamp-3",
        isHeader
          ? "text-black bg-slate-200 border-gray-100"
          : "text-accent-foreground bg-white border-accent hover:bg-gray-50 focus:border-blue-600"
      )}
      tabIndex={0}
      onKeyDown={handleKeyboardDownEvent}
    >
      {hasOverflow ? (
        <WithTooltip message={text}>
          <span>{text.slice(0, THRESHOLD)}...</span>
        </WithTooltip>
      ) : (
        <span>{text}</span>
      )}
    </div>
  );
}
