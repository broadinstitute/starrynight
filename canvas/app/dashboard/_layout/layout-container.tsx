import React from "react";

type TLayoutContainer = React.PropsWithChildren;

export function LayoutContainer(props: TLayoutContainer) {
  const { children } = props;

  return (
    <div className="h-screen w-screen bg-[#eee] flex p-3">
      <div className="flex flex-col flex-1 bg-white rounded-2xl p-4 md:px-8">
        {children}
      </div>
    </div>
  );
}
