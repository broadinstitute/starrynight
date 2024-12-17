import { Skeleton } from "@/components/ui/skeleton";
import { JobsSkeleton } from "./jobs-skeleton";

export function SidebarSkeleton() {
  return (
    <div className="space-y-2 md:pt-4 md:col-span-3">
      <Skeleton className="h-8 w-[80%]" />
      <Skeleton className="h-8 w-[30%]" />
      <Skeleton className="h-8 w-[50%]" />
      <Skeleton className="h-8 w-[70%]" />
    </div>
  );
}
