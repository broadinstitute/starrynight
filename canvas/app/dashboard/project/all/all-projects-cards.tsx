"use client";
import { Card } from "@/components/custom/card";
import { AllProjectContainer } from "./all-projects-container";
import { useRouter } from "next/navigation";
import { PROJECT_URL } from "@/constants/routes";
import { TProject } from "@/services/projects";

export type TAllProjectsCardsProps = {
  projects: TProject[];
};

export function AllProjectsCards(props: TAllProjectsCardsProps) {
  const { projects } = props;
  const { push } = useRouter();

  return (
    <AllProjectContainer>
      {projects.map(({ id, name, description, img_uri }) => (
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
    </AllProjectContainer>
  );
}
