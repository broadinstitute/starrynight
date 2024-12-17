import { Skeleton } from "@/components/ui/skeleton";
import { SidebarSkeleton } from "./sidebar";
import { ProjectMainContainer } from "../main-container";
import { JobsSkeleton } from "./jobs-skeleton";

export function ProjectSkeleton() {
  return (
    <div className="">
      <div className="flex mt-3 pb-8 md:mt-6 md:border-b md:border-b-slate-200">
        <Skeleton className="h-12 w-[400px]" />
      </div>
      <ProjectMainContainer>
        <SidebarSkeleton />
        <JobsSkeleton />
      </ProjectMainContainer>
    </div>
  );
}
