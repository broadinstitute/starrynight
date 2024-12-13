"use client";
import {
  Alert as ShadcnAlert,
  AlertDescription,
  AlertTitle,
} from "@/components/ui/alert";
import { ExclamationTriangleIcon } from "@radix-ui/react-icons";
import { CheckCircle } from "lucide-react";
import React from "react";

export type TAlertProps = {
  variant: "default" | "destructive";
  title: React.ReactNode;
  description: React.ReactNode;
};

export function Alert(props: TAlertProps) {
  const { variant, title, description } = props;

  return (
    <ShadcnAlert variant={variant}>
      {variant === "destructive" ? (
        <ExclamationTriangleIcon className="h-4 w-4" />
      ) : (
        <CheckCircle className="h-4 w-4" />
      )}
      <AlertTitle>{title}</AlertTitle>
      <AlertDescription>{description}</AlertDescription>
    </ShadcnAlert>
  );
}
