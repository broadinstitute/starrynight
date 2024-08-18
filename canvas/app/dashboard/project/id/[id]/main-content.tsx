"use client";
import useSWR from "swr";
import { Breadcrumb } from "@/components/custom/breadcrumb";
import { PageHeading } from "@/components/custom/page-heading";
import { PROJECTS_LISTING_URL } from "@/constants/routes";
import { Steps } from "./steps";
import { TProject } from "@/services/projects";
import { ProjectError } from "./project-error";
import { getSteps } from "@/services/step";
import { PageSpinner } from "@/components/custom/page-spinner";

export type TProjectMainContentProps = {
  project: TProject;
};

export function ProjectMainContent(props: TProjectMainContentProps) {
  const { project } = props;

  const { data, error, isLoading } = useSWR(
    `/step/?project_id=${project.id}`,
    () => getSteps({ projectId: project.id, canThrowOnError: true }),
    {
      revalidateIfStale: false,
      revalidateOnFocus: false,
      revalidateOnReconnect: false,
      refreshInterval: 1000 * 60 * 2,
    }
  );

  return (
    <div className="flex flex-col flex-1 overflow-auto">
      <PageHeading heading={project.name} />
      <Breadcrumb
        links={[
          { title: "All Projects", href: PROJECTS_LISTING_URL },
          { title: project.name },
        ]}
      />

      {!data?.ok && isLoading && <PageSpinner />}
      {!data?.ok && error && !isLoading && <ProjectError />}

      {data && data.ok && data.response && <Steps steps={data.response} />}
    </div>
  );
}
