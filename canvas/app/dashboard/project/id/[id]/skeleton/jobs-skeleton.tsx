import { Skeleton } from "@/components/ui/skeleton";

export function JobsSkeleton() {
  return (
    <div className="flex-1">
      <Skeleton className="h-96 w-full" />
    </div>
  );
}
