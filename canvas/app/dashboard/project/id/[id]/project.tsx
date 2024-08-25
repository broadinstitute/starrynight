"use client";

import { Breadcrumb } from "@/components/custom/breadcrumb";
import { PageHeading } from "@/components/custom/page-heading";
import { PROJECTS_LISTING_URL } from "@/constants/routes";
import { TProject } from "@/services/projects";
import { ProjectStoreProvider } from "@/stores/project";
import { StepsContainer } from "./steps-container";
import { ProjectActions } from "./project-actions";
import { TakeCredentials } from "./take-credentials";

export type TProjectMainContentProps = {
  project: TProject;
};

export function ProjectMainContent(props: TProjectMainContentProps) {
  const { project } = props;

  return (
    <ProjectStoreProvider project={project}>
      <div className="flex flex-col flex-1 overflow-auto">
        <PageHeading
          heading={project.name}
          primaryAction={<TakeCredentials projectId={project.id} />}
        />
        <Breadcrumb
          links={[
            { title: "All Projects", href: PROJECTS_LISTING_URL },
            { title: project.name },
          ]}
        />
        <div className="flex flex-1 flex-col overflow-auto">
          <div className="py-4">
            <p>{project.description}</p>
            <div className="flex justify-end">
              <ProjectActions />
            </div>
          </div>
          <StepsContainer />
        </div>
      </div>
    </ProjectStoreProvider>
  );
}
