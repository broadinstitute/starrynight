import clsx from "clsx";
import { useCreateNewProjectStore } from "./store";
import { CheckIcon } from "lucide-react";

const steps = [
  {
    id: 0,
    text: "Project",
  },
  {
    id: 1,
    text: "Experiment",
  },
];

export function CreateNewProjectCounter() {
  const { currentStep } = useCreateNewProjectStore((store) => ({
    currentStep: store.currentStep,
  }));

  return (
    <div>
      <ul className="flex flex-col text-sm gap-y-4">
        {steps.map((step, idx) => (
          <li key={step.id} className="inline-flex gap-x-3 items-center">
            <div
              className={clsx(
                "h-8 w-8 rounded-full inline-flex justify-center items-center",
                currentStep === step.id
                  ? "bg-black text-white"
                  : "bg-accent text-accent-foreground"
              )}
            >
              {currentStep > step.id ? (
                <CheckIcon className="h-4 w-4" />
              ) : (
                idx + 1
              )}
            </div>
            <div
              className={clsx(
                currentStep === step.id && "font-bold",
                currentStep !== step.id && "text-slate-400"
              )}
            >
              {step.text}
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}
