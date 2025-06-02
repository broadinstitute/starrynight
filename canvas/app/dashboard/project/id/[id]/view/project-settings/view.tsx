import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { AWSCredentialsTab } from "./aws-credentials-tab";
import { UpdateExperimentTab } from "./update-experiment";
import { ProjectViewTab } from "./project-view";

export function ProjectSettingsView() {
  return (
    <div className="flex-1 flex py-4">
      <Tabs defaultValue="aws-credentials">
        <TabsList>
          <TabsTrigger value="aws-credentials">AWS Credentials</TabsTrigger>
          <TabsTrigger value="update-experiment">Update Experiment</TabsTrigger>
          <TabsTrigger value="project-view">Project View</TabsTrigger>
        </TabsList>
        <AWSCredentialsTab />
        <UpdateExperimentTab />
        <ProjectViewTab />
      </Tabs>
    </div>
  );
}
