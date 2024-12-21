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
  headerIcon?: React.ReactNode;
  hasCloseButtonInFooter?: boolean;
  contentProps?: Omit<DialogContentProps, "children">;
  headerProps?: Omit<DialogTitleProps, "children">;
  footerProps?: Omit<React.HTMLProps<HTMLDivElement>, "children">;
  open?: boolean;
  onOpenChange?: (state: boolean) => void;
};

export const ModalCloseTrigger = DialogClose;

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
    open,
    headerIcon,
    onOpenChange,
  } = props;

  const { className: contentClassName, ...contentRest } = contentProps;
  const { className: headerClassName, ...headerRest } = headerProps;
  const { className: footerClassName, ...footerRest } = footerProps;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogTrigger asChild>{trigger}</DialogTrigger>
      <DialogContent
        className={clsx(
          "sm:max-w-md max-h-full overflow-auto",
          contentClassName
        )}
        {...contentRest}
      >
        <DialogHeader className="">
          <DialogTitle
            className={clsx(
              "mb-2 pb-3 border-b border-b-accent text-left flex space-x-2 items-center",
              headerClassName
            )}
            {...headerRest}
          >
            {headerIcon && <div>{headerIcon}</div>}
            <span>{title}</span>
          </DialogTitle>
        </DialogHeader>
        {children}

        <DialogFooter
          className={clsx(
            "sm:justify-start md:justify-between border-t border-t-accent pt-4",
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
