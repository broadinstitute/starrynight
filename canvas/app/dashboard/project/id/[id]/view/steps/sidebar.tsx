import { TStep } from "@/services/step";
import { useProjectStore } from "@/stores/project";
import React from "react";
import { ProjectSidebarRunStep } from "./run-step";
import { ProjectSidebarDeleteStep } from "./delete-step";
import { ProjectSidebarAddStep } from "./add-step";
import { Sidebar } from "@/components/custom/sidebar";
import { useRouter, useSearchParams } from "next/navigation";
import { CURRENT_STEP_QUERY_PARAMETER } from "@/constants/searchparams";

export type TStepSidebarProps = {
  steps: TStep[];
};

export function StepSidebar(props: TStepSidebarProps) {
  const { steps } = props;
  const { currentStep, updateCurrentStep } = useProjectStore((state) => ({
    currentStep: state.currentStep,
    updateCurrentStep: state.updateCurrentStep,
  }));

  const router = useRouter();
  const searchParams = useSearchParams();

  const handleOnStepUpdateRequest = React.useCallback(
    (step: TStep) => {
      updateCurrentStep(step);
      router.push(`?${CURRENT_STEP_QUERY_PARAMETER}=${step.id}`);
    },
    [updateCurrentStep, router]
  );

  const sidebarItems = React.useMemo(() => {
    const _items = steps.map((step) => ({
      title: step.name,
      id: step.id,
      onClick: () => handleOnStepUpdateRequest(step),
      actions: (
        <div className="inline-flex">
          <ProjectSidebarRunStep stepId={step.id} />
          <ProjectSidebarDeleteStep stepName={step.name} stepId={step.id} />
        </div>
      ),
    }));

    _items.push({
      title: "Add a new step",
      id: "add_new_step",
      onClick: () => console.log("Not implemented"),
      actions: (
        <div className="flex">
          <ProjectSidebarAddStep />
        </div>
      ),
    });

    return _items;
  }, [steps]);

  React.useEffect(() => {
    if (!currentStep) {
      const id = searchParams.get(CURRENT_STEP_QUERY_PARAMETER);
      const step = steps.find((s) => `${s.id}` === id) || steps[0];
      handleOnStepUpdateRequest(step);
    }
  }, []);

  return (
    <Sidebar
      className="md:pt-4 md:col-span-3"
      activeItemId={currentStep?.id}
      items={sidebarItems}
    />
  );
}
