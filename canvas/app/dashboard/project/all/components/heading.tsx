import { ActionContainer } from "@/app/dashboard/_layout/action-container";
import { PageHeading } from "@/components/custom/page-heading";
import { CreateProject } from "./create-project";

export function AllProjectsHeading() {
  return (
    <PageHeading heading="All Projects">
      <ActionContainer>
        <CreateProject />
      </ActionContainer>
    </PageHeading>
  );
}
