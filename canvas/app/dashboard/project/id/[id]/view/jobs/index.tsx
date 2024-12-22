import { useGetJobs } from "@/services/job";
import { useProjectStore } from "@/stores/project";
import { JobsSkeleton } from "../skeleton/jobs-skeleton";
import { Button, buttonVariants } from "@/components/ui/button";
import Link from "next/link";
import { PROJECTS_LISTING_URL } from "@/constants/routes";
import { ProjectJobsView } from "./view";

export function ProjectJobs() {
  const { currentStep } = useProjectStore((state) => ({
    currentStep: state.currentStep,
  }));

  const { data, isLoading, error } = useGetJobs({ stepId: currentStep?.id });

  if (isLoading || !currentStep) {
    return <JobsSkeleton />;
  }

  if (error || !data) {
    return (
      <div className="p-4 flex-col flex justify-center items-center text-red-500 md:pr-0 md:col-span-9 md:border-l md:border-l-slate-100">
        <p>
          Failed to load jobs for the current step. Please reload the page or
          try again after sometime.
        </p>
        <div className="mt-4 space-x-4">
          <Button onClick={() => (window.location.href = window.location.href)}>
            Refresh
          </Button>
          <Link
            href={PROJECTS_LISTING_URL}
            className={buttonVariants({ variant: "default" })}
          >
            See all projects
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="p-4 md:pr-0 md:col-span-9 md:border-l md:border-l-slate-100">
      <ProjectJobsView step={currentStep} jobs={data} />
    </div>
  );
}
