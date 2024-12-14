import Image, { ImageProps } from "next/image";
import { Button, ButtonProps } from "@/components/ui/button";
import { ChevronRight } from "lucide-react";
import { ErrorBoundary } from "next/dist/client/components/error-boundary";
import clsx from "clsx";
import React from "react";

export type TCardProps = {
  img: {
    alt: string;
    src: string;
  };
  title: string;
  description: string;
  action?: ButtonProps;
  className?: string;
};

type TCardImageProps = {
  className?: string;
  src: string;
  alt: string;
};

function CardImage(props: TCardImageProps) {
  const { className, src, alt } = props;

  return (
    <Image
      src={src}
      alt={alt}
      fill
      className={clsx("object-cover", className)}
    />
  );
}

export function Card(props: TCardProps) {
  const { img, title, description, action, className, ...rest } = props;

  return (
    <div
      className={clsx(
        "border rounded-md overflow-hidden transition hover:shadow-sm",
        className
      )}
      {...rest}
    >
      <div className="rounded-md overflow-hidden flex relative h-40">
        <ErrorBoundary
          errorComponent={() => (
            <CardImage src="/project-placeholder.webp" alt="project" />
          )}
        >
          <CardImage src={img.src} alt={img.alt} />
        </ErrorBoundary>
      </div>
      <div className="p-2">
        <span className="font-bold">{title}</span>
        <p className="mt-4 font-light">{description}</p>
      </div>
      {action && (
        <div className="flex justify-end">
          <Button size="icon" variant="ghost" {...action}>
            <ChevronRight />
          </Button>
        </div>
      )}
    </div>
  );
}
