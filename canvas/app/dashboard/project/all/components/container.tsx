import { PageContainer } from "@/app/dashboard/_layout/page-container";

export function AllProjectsContainer(props: React.PropsWithChildren) {
  const { children } = props;
  return (
    <PageContainer className="gap-8 py-0  grid grid-cols-1 md:py-8 md:px-0 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
      {children}
    </PageContainer>
  );
}
