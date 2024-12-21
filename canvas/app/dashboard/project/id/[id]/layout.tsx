import React, { Suspense } from "react";
import { ProjectSkeleton } from "./view/skeleton";

export default function ProjectLayout(props: React.PropsWithChildren) {
  const { children } = props;

  return <Suspense fallback={<ProjectSkeleton />}>{children}</Suspense>;
}
