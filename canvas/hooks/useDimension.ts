import React from "react";
import { useDebouncedCallback } from "use-debounce";

export type TUseDimensionOptions = {
  ref: React.RefObject<HTMLElement>;
};

export function useDimension(options: TUseDimensionOptions) {
  const { ref } = options;

  const [width, setWidth] = React.useState(0);
  const [height, setHeight] = React.useState(0);

  const handleOnResize = useDebouncedCallback((element: HTMLElement) => {
    const rect = element.getBoundingClientRect();

    setWidth(rect.width);
    setHeight(rect.height);
  }, 1000);

  React.useEffect(() => {
    const element = ref.current;

    if (!element) return;

    const resizeObserver = new ResizeObserver(() => handleOnResize(element));
    resizeObserver.observe(element);

    return () => {
      resizeObserver.disconnect();
    };
  }, [ref, handleOnResize]);

  return {
    height,
    width,
  };
}
