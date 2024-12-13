import { Skeleton } from "@/components/ui/skeleton";

export function SkeletonCard() {
  return (
    <div className="inline-flex flex-col space-y-3">
      <Skeleton className="h-[160px] rounded-xl" />
      <div className="space-y-2">
        <Skeleton className="h-4 w-[80%]" />
        <Skeleton className="h-4 w-[40%]" />
        <Skeleton className="h-4 w-[70%]" />
        <Skeleton className="h-4 w-[30%]" />
      </div>
    </div>
  );
}
