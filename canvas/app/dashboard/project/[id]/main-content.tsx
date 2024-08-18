import { Breadcrumb } from "@/components/custom/breadcrumb";
import { PageHeading } from "@/components/custom/page-heading";
import { PROJECTS_LISTING_URL } from "@/constants/routes";
import { Steps } from "./steps";

export function ProjectMainContent() {
  return (
    <div className="flex flex-col flex-1 overflow-auto">
      <PageHeading heading="Project 1" />
      <Breadcrumb
        links={[
          { title: "All Projects", href: PROJECTS_LISTING_URL },
          { title: "Project 1" },
        ]}
      />
      <Steps
        steps={[
          {
            title: "01_CP/Illumination correction",
          },
          {
            title: "02_CP/Illumination apply",
          },
          {
            title: "03_CP/Segmentation",
          },
          {
            title: "04_SBS/Illumination correction",
          },
        ]}
      />
    </div>
  );
}
