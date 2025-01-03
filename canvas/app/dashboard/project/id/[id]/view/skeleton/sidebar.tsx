import { Skeleton } from "@/components/ui/skeleton";

export function SidebarSkeleton() {
  return (
    <div className="space-y-2 md:pt-4 md:col-span-3">
      {Array.from({ length: 8 })
        .fill(0)
        .map((_, idx) => (
          <div className="flex gap-2" key={idx}>
            <Skeleton className="h-8 w-[80%]" />
            <Skeleton className="h-8 w-[10%]" />
            <Skeleton className="h-8 w-[10%]" />
          </div>
        ))}
    </div>
  );
}
