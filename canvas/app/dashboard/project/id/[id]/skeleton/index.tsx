import { Skeleton } from "@/components/ui/skeleton";
import { StepAndJobsSkeleton } from "./step-and-jobs-skeleton";

export function ProjectSkeleton() {
  return (
    <div className="">
      <div className="flex mt-3 pb-8 md:mt-6 md:border-b md:border-b-slate-200">
        <Skeleton className="h-12 w-[400px]" />
      </div>
      <div className="py-2">
        <Skeleton className="h-6 w-96" />
      </div>
      <StepAndJobsSkeleton />
    </div>
  );
}
