import { Skeleton } from "@/components/ui/skeleton";
import { JobsSkeleton } from "./jobs-skeleton";

export function StepAndJobsSkeleton() {
  return (
    <div className="flex flex-col py-4 gap-4 md:flex-row">
      <div className="space-y-3">
        <Skeleton className="h-8 w-64" />
        <Skeleton className="h-8 w-64" />
        <Skeleton className="h-8 w-64" />
        <Skeleton className="h-8 w-64" />
      </div>
      <JobsSkeleton />
    </div>
  );
}
