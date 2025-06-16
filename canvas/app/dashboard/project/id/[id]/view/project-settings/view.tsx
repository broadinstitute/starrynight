import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { AWSCredentialsTab } from "./aws-credentials-tab";
import { UpdateExperimentTab } from "./update-experiment";
import { ProjectViewTab } from "./project-view";

export type ProjectSettingsViewProps = {
  onRequestClose: () => void;
};

export function ProjectSettingsView(props: ProjectSettingsViewProps) {
  const { onRequestClose } = props;

  return (
    <div className="flex-1 flex py-4">
      <Tabs className="flex flex-col flex-1" defaultValue="aws-credentials">
        <TabsList className="justify-start">
          <TabsTrigger value="aws-credentials">AWS Credentials</TabsTrigger>
          <TabsTrigger value="update-experiment">Update Experiment</TabsTrigger>
          <TabsTrigger value="project-view">Project View</TabsTrigger>
        </TabsList>
        <div className="flex-1 overflow-auto py-4">
          <AWSCredentialsTab />
          <UpdateExperimentTab onRequestClose={onRequestClose} />
          <ProjectViewTab />
        </div>
      </Tabs>
    </div>
  );
}
