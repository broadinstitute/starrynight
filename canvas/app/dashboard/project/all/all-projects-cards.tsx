"use client";
import { Card } from "@/components/custom/card";
import { AllProjectContainer } from "./all-projects-container";
import { useRouter } from "next/navigation";
import { PROJECT_URL } from "@/constants/routes";

export type TAllProjectsCardsProps = {
  projects: {
    id: string;
    imgSrc: string;
    title: string;
    description: string;
  }[];
};

export function AllProjectsCards(props: TAllProjectsCardsProps) {
  const { projects } = props;
  const { push } = useRouter();

  return (
    <AllProjectContainer>
      {projects.map(({ id, title, description, imgSrc }) => (
        <Card
          key={id}
          img={{
            alt: title,
            src: imgSrc,
          }}
          description={description}
          title={title}
          action={{
            onClick: () => push(`${PROJECT_URL}/${id}`),
          }}
        />
      ))}
    </AllProjectContainer>
  );
}
