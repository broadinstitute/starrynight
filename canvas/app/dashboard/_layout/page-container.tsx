import React from "react";

export type TPageContainer = React.PropsWithChildren;

export function PageContainer(props: TPageContainer) {
  const { children } = props;

  return (
    <div className="px-0 py-4 md:px-4 flex flex-col flex-1 overflow-auto relative">
      {children}
    </div>
  );
}
