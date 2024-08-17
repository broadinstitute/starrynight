import { AllProjectsCards } from "./all-projects-cards";
import { NoProjects } from "./no-projects";

async function fetchProject() {
  const projects =
    Date.now() % 2
      ? [
          {
            id: "1",
            description: "This is the description for project 1",
            title: "Project",
            imgSrc: "/test.png",
          },
        ]
      : [];

  await new Promise((resolve) => setTimeout(resolve, 1000));
  return {
    ok: true,
    data: projects,
  };
}

export async function AllProjects() {
  const response = await fetchProject();

  if (!response.ok) {
    return <div>Error</div>;
  }

  if (response.data.length === 0) {
    return <NoProjects />;
  }

  return <AllProjectsCards projects={response.data} />;
}
