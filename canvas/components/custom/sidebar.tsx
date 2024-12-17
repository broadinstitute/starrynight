import React from "react";
import { Button } from "../ui/button";
import { cn } from "@/shadcn/utils";

export type TSidebarItem = {
  id: string | number;
  title: string;
  onClick: () => void;
  actions?: React.ReactNode;
};

export type TSidebarProps = React.HTMLProps<HTMLDivElement> & {
  items: TSidebarItem[];
  activeItemId?: string | number;
};

export function Sidebar(props: TSidebarProps) {
  const { items, activeItemId, ...rest } = props;

  return (
    <aside aria-label="Sidebar" {...rest}>
      <ul className="space-y-2 font-medium">
        {items.map(({ id, onClick, title, actions }) => (
          <li
            key={id}
            className={cn(
              "flex items-center pl-4 rounded-md",
              activeItemId === id
                ? "bg-accent text-accent-foreground"
                : "hover:bg-accent hover:text-accent-foreground cursor-pointer"
            )}
            onClick={onClick}
          >
            <div className="w-full text-sm inline items-center text-left text-ellipsis truncate overflow-hidden">
              {title}
            </div>
            {actions}
          </li>
        ))}
      </ul>
    </aside>
  );
}
