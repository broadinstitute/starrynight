import { Skeleton } from "@/components/ui/skeleton";

export function SkeletonCard() {
  return (
    <div className="inline-flex flex-col space-y-3 max-w-[250px]">
      <Skeleton className="h-[160px] w-[250px] rounded-xl" />
      <div className="space-y-2">
        <Skeleton className="h-4 w-[250px]" />
        <Skeleton className="h-4 w-[170px]" />
        <Skeleton className="h-4 w-[120px]" />
        <Skeleton className="h-4 w-[150px]" />
      </div>
    </div>
  );
}
