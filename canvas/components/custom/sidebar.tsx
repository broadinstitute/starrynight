import React from "react";
import { Button } from "../ui/button";
import { cn } from "@/shadcn/utils";

export type TSidebarItem = {
  title: string;
  onClick: () => void;
};

export type TSidebarProps = {
  items: TSidebarItem[];
};

export function Sidebar(props: TSidebarProps) {
  const { items } = props;

  return (
    <div>
      <aside className={cn("w-64 transition-transform")} aria-label="Sidebar">
        <ul className="space-y-2 font-medium">
          {items.map(({ onClick, title }) => (
            <li key={title}>
              <Button
                variant="ghost"
                className="w-full justify-start"
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
