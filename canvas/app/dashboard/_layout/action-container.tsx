"use client";

import clsx from "clsx";
import React from "react";

export type TActionContainerProps = React.HTMLProps<HTMLDivElement> & {
  buttonsContainer?: React.HTMLProps<HTMLDivElement>;
};

export function ActionContainer(props: TActionContainerProps) {
  const { children, className, buttonsContainer, ...rest } = props;
  const ref = React.useRef<HTMLDivElement>(null);

  const handleOnResize = React.useCallback(() => {
    if (!ref.current) return;

    const mainWrapper = document.querySelector(
      "#main-wrapper"
    ) as HTMLDivElement;
    if (!mainWrapper) return;

    if (window.innerWidth > 768) {
      mainWrapper.style.paddingBottom = "0px";
      return;
    }

    mainWrapper.style.paddingBottom = `${
      ref.current.getBoundingClientRect().height
    }px`;
  }, []);

  React.useEffect(() => {
    handleOnResize();

    window.addEventListener("resize", handleOnResize);

    return () => {
      window.removeEventListener("resize", handleOnResize);
    };
  }, [handleOnResize]);

  return (
    <div
      className={clsx(
        "fixed z-50 bottom-0 left-0 right-0 flex flex-col md:relative md:w-full md:flex-1",
        className
      )}
      ref={ref}
      {...rest}
    >
      <div className="bg-[#eee] px-3 md:hidden">
        <div className="bg-white h-8 rounded-b-2xl"></div>
      </div>
      <div
        {...buttonsContainer}
        className={clsx(
          "bg-[#eee] mx-3 grid gap-2 px-2 py-4 md:bg-transparent md:flex md:p-0 md:justify-end md:flex-wrap",
          buttonsContainer?.className
        )}
      >
        {children}
      </div>
    </div>
  );
}
