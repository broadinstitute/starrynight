import Image from "next/image";
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
  className?: string;
  onClick?: () => void;
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
  const { img, title, description, className, onClick, ...rest } = props;

  return (
    <div
      onClick={onClick}
      className={clsx(
        "border rounded-md md:max-h-80 overflow-hidden transition hover:border-[#b8cadd] hover:shadow-sm hover:scale-[1.01] hover:cursor-pointer",
        className
      )}
      tabIndex={0}
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
        <p className="mt-4 font-light pb-16">{description}</p>
      </div>
    </div>
  );
}
