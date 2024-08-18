import React from "react";
import { Button } from "../ui/button";
import { cn } from "@/shadcn/utils";

export type TSidebarItem = {
  id: string | number;
  title: string;
  onClick: () => void;
};

export type TSidebarProps = {
  items: TSidebarItem[];
  active: string | number;
};

export function Sidebar(props: TSidebarProps) {
  const { items, active } = props;

  return (
    <div className="overflow-y-auto pr-4">
      <aside
        className={cn("w-full md:w-64 transition-transform")}
        aria-label="Sidebar"
      >
        <ul className="space-y-2 font-medium">
          {items.map(({ id, onClick, title }) => (
            <li key={id}>
              <Button
                variant={active === id ? "default" : "ghost"}
                className={cn(
                  "w-full inline text-left text-ellipsis truncate overflow-hidden",
                  active === id ? "pointer-events-none" : ""
                )}
                onClick={onClick}
              >
                {title}
              </Button>
            </li>
          ))}
        </ul>
      </aside>
    </div>
  );
}
