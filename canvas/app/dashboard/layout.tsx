import React from "react";
import { LayoutContainer } from "./_layout/layout-container";
import { Navbar } from "./_layout/navbar";

type TDashboardLayout = React.PropsWithChildren;

export default function DashboardLayout(props: TDashboardLayout) {
  const { children } = props;

  return (
    <LayoutContainer>
      <Navbar />
      {children}
    </LayoutContainer>
  );
}
