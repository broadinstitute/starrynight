import { Skeleton } from "@/components/ui/skeleton";

export function JobsSkeleton() {
  return (
    <div className="md:col-span-9 pl-4 pt-4 border-l border-l-slate-100">
      <div>
        <Skeleton className="h-12 w-full mb-6" />
        <div className="flex gap-4">
          <Skeleton className="flex-1 h-96"></Skeleton>
          <Skeleton className="flex-1 h-96"></Skeleton>
        </div>
      </div>
    </div>
  );
}
