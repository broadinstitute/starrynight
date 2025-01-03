import React from "react";
import { Modal } from "./modal";
import { Wrench } from "lucide-react";

export type TFeatureNotImplementedProps = {
  featureName: string;
  children: React.ReactNode;
};

export function FeatureNotImplementedModal(props: TFeatureNotImplementedProps) {
  const { featureName, children } = props;

  return (
    <Modal
      trigger={children}
      title="Feature Under Development"
      hasCloseButtonInFooter
      headerIcon={<Wrench />}
    >
      <div>
        The &quot;<span className="font-bold">{featureName}&quot;</span> feature
        is under development and will be available soon.
      </div>
    </Modal>
  );
}
