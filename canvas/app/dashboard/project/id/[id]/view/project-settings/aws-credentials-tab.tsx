import { TabsContent } from "@/components/ui/tabs";
import { useProjectStore } from "@/stores/project";
import { TakeCredentialsForm } from "./take-credentials-form";

export function AWSCredentialsTab() {
  const { project } = useProjectStore((state) => ({ project: state.project }));

  return (
    <TabsContent value="aws-credentials">
      <p className="text-gray-400">
        You can safely add your AWS credentials here. They allow us to perform
        tasks like accessing storage. This AWS credentials is used for &quot;
        {project.name}&quot;
      </p>
      <div className="py-2">
        <TakeCredentialsForm projectId={project.id} />
      </div>
    </TabsContent>
  );
}
