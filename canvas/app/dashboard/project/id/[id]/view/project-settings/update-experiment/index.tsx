import { PageSpinner } from "@/components/custom/page-spinner";
import { TabsContent } from "@/components/ui/tabs";
import { useGetProject } from "@/services/projects";
import { useProjectStore } from "@/stores/project";
import { UpdateExperimentView } from "./view";
import { useEffect } from "react";

export type UpdateExperimentTabProps = {
  onRequestClose: () => void;
};

export function UpdateExperimentTab(props: UpdateExperimentTabProps) {
  const { onRequestClose } = props;
  const projectID = useProjectStore((state) => state.project.id);
  const { data, error, isLoading, refetch } = useGetProject({
    id: projectID,
  });

  useEffect(() => {
    refetch();
  }, [refetch]);

  if (isLoading) {
    return (
      <TabsContent value="update-experiment">
        <div className="p-4">
          <PageSpinner />
        </div>
      </TabsContent>
    );
  }
  if (!data || error) {
    return (
      <TabsContent value="update-experiment">
        <div className="text-red-500">
          Something went wrong! Please try after sometime.
        </div>
      </TabsContent>
    );
  }

  return (
    <TabsContent value="update-experiment">
      <UpdateExperimentView onRequestClose={onRequestClose} project={data} />
    </TabsContent>
  );
}
