import { Skeleton } from "@/components/ui/skeleton";

export function JobsSkeleton() {
  return (
    <div className="md:col-span-9 pl-4 pt-4 border-l border-l-slate-100">
      <Skeleton className="h-96 w-full" />
    </div>
  );
}
