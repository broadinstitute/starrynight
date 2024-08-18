import { Button } from "@/components/ui/button";
import { PROJECTS_LISTING_URL } from "@/constants/routes";
import Link from "next/link";

export function ProjectError() {
  return (
    <div className="flex-1 flex flex-col justify-center items-center font-thin text-3xl">
      <p className="text-center">
        We&apos;re experiencing a temporary issue. Please try again shortly.
      </p>
      <Link href={PROJECTS_LISTING_URL} className="mt-4">
        <Button>See All Projects</Button>
      </Link>
    </div>
  );
}
