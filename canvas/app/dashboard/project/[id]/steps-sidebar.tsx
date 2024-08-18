"use client";

import { Sidebar } from "@/components/custom/sidebar";

export function StepSidebar() {
  return (
    <Sidebar
      items={[
        {
          onClick: () => console.log("01_CP/Illumination correction"),
          title: "01_CP/Illumination correction",
        },
        {
          onClick: () => console.log("02_CP/Illumination apply"),
          title: "02_CP/Illumination apply",
        },
        {
          onClick: () => console.log("03_CP/Segmentation"),
          title: "03_CP/Segmentation",
        },
        {
          onClick: () => console.log("04_SBS/Illumination correction"),
          title: "04_SBS/Illumination correction",
        },
      ]}
    />
  );
}
