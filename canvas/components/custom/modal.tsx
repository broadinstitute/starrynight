"use client";

import React from "react";
import {
  Dialog,
  DialogContent,
  DialogTrigger,
  DialogHeader,
  DialogTitle,
  DialogClose,
  DialogFooter,
} from "@/components/ui/dialog";

import { Button } from "@/components/ui/button";
import { DialogContentProps, DialogTitleProps } from "@radix-ui/react-dialog";
import clsx from "clsx";

export type TModalProps = {
  title: string;
  trigger: React.ReactNode;
  children: React.ReactNode;
  actions?: React.ReactNode[];
  hasCloseButtonInFooter?: boolean;
  contentProps?: Omit<DialogContentProps, "children">;
  headerProps?: Omit<DialogTitleProps, "children">;
  footerProps?: Omit<React.HTMLProps<HTMLDivElement>, "children">;
};

export function Modal(props: TModalProps) {
  const {
    title,
    trigger,
    children,
    actions,
    hasCloseButtonInFooter,
    contentProps = {},
    footerProps = {},
    headerProps = {},
  } = props;

  const { className: contentClassName, ...contentRest } = contentProps;
  const { className: headerClassName, ...headerRest } = headerProps;
  const { className: footerClassName, ...footerRest } = footerProps;

  return (
    <Dialog>
      <DialogTrigger asChild>{trigger}</DialogTrigger>
      <DialogContent
        className={clsx(
          "sm:max-w-md max-h-full overflow-auto",
          contentClassName
        )}
        {...contentRest}
      >
        <DialogHeader>
          <DialogTitle
            className={clsx("mb-2 text-left", headerClassName)}
            {...headerRest}
          >
            {title}
          </DialogTitle>
        </DialogHeader>
        {children}

        <DialogFooter
          className={clsx(
            "sm:justify-start md:justify-between",
            footerClassName
          )}
          {...footerRest}
        >
          {hasCloseButtonInFooter && (
            <DialogClose asChild>
              <Button variant="secondary">Close</Button>
            </DialogClose>
          )}
          {actions}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
