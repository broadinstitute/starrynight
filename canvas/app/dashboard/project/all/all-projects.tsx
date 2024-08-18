import { getProjects } from "@/services/projects";
import { AllProjectsCards } from "./all-projects-cards";
import { NoProjects } from "./no-projects";
import { AllProjectError } from "./all-project-error";

async function fetchProject() {
  const response = await getProjects();

  return {
    ok: true,
    data: response.response,
  };
}

export async function AllProjects() {
  const response = await fetchProject();

  if (!response.ok || !Array.isArray(response.data)) {
    return <AllProjectError />;
  }

  if (response.data.length === 0) {
    return <NoProjects />;
  }

  return <AllProjectsCards projects={response.data} />;
}
