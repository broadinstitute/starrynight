import { PageHeading } from "@/components/custom/page-heading";
import { CreateProject } from "./create-project";

export function AllProjectsHeading() {
  return (
    <PageHeading heading="All Projects" primaryAction={<CreateProject />} />
  );
}
