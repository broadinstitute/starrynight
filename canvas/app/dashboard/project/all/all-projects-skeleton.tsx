import { SkeletonCard } from "@/components/custom/card-skeleton";
import { AllProjectContainer } from "./all-projects-container";

export function AllProjectSkeleton() {
  return (
    <AllProjectContainer>
      <SkeletonCard />
      <SkeletonCard />
      <SkeletonCard />
    </AllProjectContainer>
  );
}
