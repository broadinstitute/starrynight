import { TJob } from "@/services/job";
import { ProjectJobRun } from "./run-job";
import { ProjectRuns } from "../runs";
import { ProjectJobInputs } from "./job-inputs";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { useProjectStore } from "@/stores/project";
import { ProjectRunBadge } from "../runs/badge";

export type TProjectJobProps = {
  job: TJob;
};

export function ProjectJob(props: TProjectJobProps) {
  const { job } = props;
  const { jobStatus } = useProjectStore((store) => ({
    jobStatus: store.jobStatus,
  }));

  return (
    <div>
      <Accordion
        className="flex flex-col p-2 rounded-md border border-accent"
        type="single"
        collapsible
      >
        <AccordionItem
          value={job.id as string}
          className="border-b-transparent"
        >
          <div className="flex items-center justify-between">
            <ProjectJobRun job={job} />
            &nbsp;
            <AccordionTrigger className="font-semibold flex-1">
              {job.name}
              <span className="ml-auto mr-4">
                <ProjectRunBadge status={jobStatus[job.id]} />
              </span>
            </AccordionTrigger>
          </div>
          <AccordionContent className="p-4">
            <ProjectJobInputs job={job} />
            <hr className="my-4 border-t-accent" />
            {job.description && (
              <p className="py-2 text-sm">{job.description}</p>
            )}
            <ProjectRuns job={job} />
          </AccordionContent>
        </AccordionItem>
      </Accordion>

      <div className="hidden">
        <ProjectRuns job={job} />
      </div>
    </div>
  );
}
