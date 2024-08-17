"use client";
import { Card } from "@/app/_components/card";
import { AllProjectContainer } from "./all-projects-container";

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
            onClick: () => console.log("Opening project" + id),
          }}
        />
      ))}
    </AllProjectContainer>
  );
}
