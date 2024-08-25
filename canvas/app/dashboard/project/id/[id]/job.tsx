import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { TProjectStepJob } from "@/services/job";
import { ProjectStepJobRunsContainer } from "./runs-container";
import React from "react";

export type TProjectStepJobProps = {
  job: TProjectStepJob;
};

export function ProjectStepJob(props: TProjectStepJobProps) {
  const { job } = props;

  return (
    <Accordion type="single" collapsible>
      <AccordionItem value="item-1">
        <AccordionTrigger className="hover:no-underline">
          {job.name}
        </AccordionTrigger>
        <AccordionContent>
          <ProjectStepJobRunsContainer job={job} />
        </AccordionContent>
      </AccordionItem>
    </Accordion>
  );
}
