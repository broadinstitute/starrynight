import Image from "next/image";
import { Button, ButtonProps } from "@/components/ui/button";
import { ChevronRight } from "lucide-react";
import { ErrorBoundary } from "next/dist/client/components/error-boundary";

export type TCardProps = {
  img: {
    alt: string;
    src: string;
  };
  title: string;
  description: string;
  action?: ButtonProps;
};

export function Card(props: TCardProps) {
  const { img, title, description, action, ...rest } = props;

  return (
    <div className="w-[250px]" {...rest}>
      <div className="rounded-md overflow-hidden">
        <ErrorBoundary
          errorComponent={() => (
            <Image
              className="object-cover object-center h-40"
              height={80}
              width={250}
              src="/project-placeholder.webp"
              alt="Project"
            />
          )}
        >
          <Image
            className="object-cover object-center h-40"
            height={80}
            width={250}
            src={img.src}
            alt={img.alt}
          />
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
