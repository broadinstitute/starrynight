"use client";
import { Card } from "@/components/custom/card";
import { useRouter } from "next/navigation";
import { PROJECT_URL } from "@/constants/routes";
import { AllProjectsContainer } from "../components/container";
import { useGetProjects } from "@/services/projects";
import { ContainerWithTextCenter } from "@/app/dashboard/_layout/container-text-center";

export function AllProjectsView() {
  const { data, error } = useGetProjects();
  const { push } = useRouter();

  if (!data || error) {
    return (
      <ContainerWithTextCenter>
        We&apos;re experiencing a temporary issue. Please try again shortly.
      </ContainerWithTextCenter>
    );
  }

  if (data.length === 0) {
    return (
      <ContainerWithTextCenter>
        You don&apos;t have any project yet! <br />
        <br />
        Use the “Create Project” button to create a new project.
      </ContainerWithTextCenter>
    );
  }

  return (
    <AllProjectsContainer>
      {data.map(({ id, name, description, img_uri }) => (
        <Card
          key={id}
          img={{
            alt: name,
            src: img_uri || "/project-placeholder.webp",
          }}
          description={description}
          title={name}
          action={{
            onClick: () => push(`${PROJECT_URL}/${id}`),
          }}
        />
      ))}
    </AllProjectsContainer>
  );
}
