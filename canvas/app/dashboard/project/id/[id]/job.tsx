import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { TProjectStepJob } from "@/services/job";
import { ProjectStepJobRunsContainer } from "./runs-container";
import React from "react";
import { useProjectStore } from "@/stores/project";

export type TProjectStepJobProps = {
  job: TProjectStepJob;
};

export function ProjectStepJob(props: TProjectStepJobProps) {
  const { step } = useProjectStore((state) => ({ step: state.currentStep }));
  const { job, ...rest } = props;

  return (
    <AccordionItem value={`job-${job.id}-${step!.id}`} {...rest}>
      <AccordionTrigger className="hover:no-underline font-bold text-xl">
        {job.name}
      </AccordionTrigger>
      <AccordionContent>
        <ProjectStepJobRunsContainer job={job} />
      </AccordionContent>
    </AccordionItem>
  );
}
