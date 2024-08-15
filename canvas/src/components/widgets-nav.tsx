"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { ArrowRightIcon } from "@radix-ui/react-icons";

import { cn } from "@/src/lib/utils";
import { ScrollArea, ScrollBar } from "@/src/components/ui/scroll-area";

const widgets = [
  // {
  //   name: "Explore",
  //   href: "/explore",
  // },
  // {
  //   name: "Download",
  //   href: "/download",
  // },
  {
    name: "Search Metadata",
    href: "/search",
  },
  {
    name: "Advance(Shell)",
    href: "/duckshell",
  },
];

interface WigetsNavProps extends React.HTMLAttributes<HTMLDivElement> { }

export function WidgetsNav({ className, ...props }: WigetsNavProps) {
  const pathname = usePathname();

  return (
    <div className="relative">
      <ScrollArea className="max-w-[600px] lg:max-w-none">
        <div className={cn("mb-4 flex items-center", className)} {...props}>
          {widgets.map((widget, index) => (
            <Link
              href={widget.href}
              key={widget.href}
              className={cn(
                "flex h-7 items-center justify-center rounded-full px-4 text-center text-sm transition-colors hover:text-primary",
                pathname?.startsWith(widget.href) ||
                  (index === 0 && pathname === "/")
                  ? "bg-muted font-medium text-primary"
                  : "text-muted-foreground"
              )}
            >
              {widget.name}
            </Link>
          ))}
        </div>
        <ScrollBar orientation="horizontal" className="invisible" />
      </ScrollArea>
    </div>
  );
}

// interface ExampleCodeLinkProps {
//   pathname: string | null
// }
//
// export function ExampleCodeLink({ pathname }: ExampleCodeLinkProps) {
//   const example = examples.find((example) => pathname?.startsWith(example.href))
//
//   if (!example?.code) {
//     return null
//   }
//
//   return (
//     <Link
//       href={example?.href}
//       target="_blank"
//       rel="nofollow"
//       className="absolute right-0 top-0 hidden items-center rounded-[0.5rem] text-sm font-medium md:flex"
//     >
//       View code
//       <ArrowRightIcon className="ml-1 h-4 w-4" />
//     </Link>
//   )
// }
