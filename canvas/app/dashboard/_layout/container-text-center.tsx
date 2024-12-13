import clsx from "clsx";
import React from "react";

export type TContainerWithTextCenterProps = React.HTMLProps<HTMLDivElement> & {
  paragraphProps?: Omit<React.HTMLProps<HTMLParagraphElement>, "children">;
};

export function ContainerWithTextCenter(props: TContainerWithTextCenterProps) {
  const { className, children, paragraphProps, ...rest } = props;
  const { className: pClassName, ...pRest } = props;

  return (
    <div
      className={clsx(
        "flex-1 flex flex-col justify-center items-center font-thin text-3xl",
        className
      )}
      {...rest}
    >
      <p className={clsx("text-center", pClassName)} {...pRest}>
        {children}
      </p>
    </div>
  );
}
