import React, { Suspense } from "react";
import ProjectLoading from "./loading";

export default function ProjectLayout(props: React.PropsWithChildren) {
  const { children } = props;

  return <Suspense fallback={<ProjectLoading />}>{children}</Suspense>;
}
