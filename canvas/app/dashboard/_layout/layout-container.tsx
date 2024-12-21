import React from "react";

type TLayoutContainer = React.PropsWithChildren;

export function LayoutContainer(props: TLayoutContainer) {
  const { children } = props;

  return (
    <div className="bg-[#eee] min-h-screen flex flex-col p-3">
      <div className="bg-white rounded-2xl p-4 h-full flex-1 w-full flex justify-center">
        <div
          id="main-wrapper"
          className="flex flex-col flex-1 max-w-[1500px]  md:px-8"
        >
          {children}
        </div>
      </div>
    </div>
  );
}
