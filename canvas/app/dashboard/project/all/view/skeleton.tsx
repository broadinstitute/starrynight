import { SkeletonCard } from "@/components/custom/card-skeleton";
import { AllProjectsContainer } from "../components/container";

export function AllProjectsSkeleton() {
  return (
    <AllProjectsContainer>
      <SkeletonCard />
      <SkeletonCard />
      <SkeletonCard />
      <SkeletonCard />
    </AllProjectsContainer>
  );
}
