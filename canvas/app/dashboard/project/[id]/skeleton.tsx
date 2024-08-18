import { PageHeading } from "@/components/custom/page-heading";
import { Skeleton } from "@/components/ui/skeleton";

export function ProjectSkeleton() {
  return (
    <div className="">
      <div className="flex mt-3 pb-8 md:mt-6 md:border-b md:border-b-slate-200">
        <Skeleton className="h-12 w-[400px]" />
      </div>

      <div className="py-2">
        <Skeleton className="h-6 w-96" />
      </div>

      <div className="flex flex-col py-4 gap-4 md:flex-row">
        <div className="space-y-3">
          <Skeleton className="h-8 w-64" />
          <Skeleton className="h-8 w-64" />
          <Skeleton className="h-8 w-64" />
          <Skeleton className="h-8 w-64" />
        </div>
        <div className="flex-1">
          <Skeleton className="h-96 w-full" />
        </div>
      </div>
    </div>
  );
}
