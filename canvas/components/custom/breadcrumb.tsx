import {
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from "@/components/ui/breadcrumb";
import Link from "next/link";
import React from "react";

export type TBreadcrumbLink = {
  href?: string;
  title: string;
};

export type TBreadcrumbProps = {
  links: TBreadcrumbLink[];
};

export function Breadcrumb(props: TBreadcrumbProps) {
  const { links } = props;

  return (
    <nav aria-label="breadcrumb" className="py-2">
      <BreadcrumbList>
        {links.map(({ href, title }) => {
          if (!href) {
            return (
              <BreadcrumbItem key={title}>
                <BreadcrumbPage>{title}</BreadcrumbPage>
              </BreadcrumbItem>
            );
          }

          return (
            <React.Fragment key={title}>
              <BreadcrumbItem>
                <BreadcrumbLink asChild>
                  <Link href={href}>{title}</Link>
                </BreadcrumbLink>
              </BreadcrumbItem>
              <BreadcrumbSeparator />
            </React.Fragment>
          );
        })}
      </BreadcrumbList>
    </nav>
  );
}
