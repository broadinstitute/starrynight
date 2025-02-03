import { ActionContainer } from "@/app/dashboard/_layout/action-container";
import { PageHeading } from "@/components/custom/page-heading";
import { buttonVariants } from "@/components/ui/button";
import { PROJECT_CREATE_NEW } from "@/constants/routes";
import clsx from "clsx";
import Link from "next/link";

export function AllProjectsHeading() {
  return (
    <PageHeading heading="All Projects">
      <ActionContainer>
        <Link
          href={PROJECT_CREATE_NEW}
          className={clsx(
            buttonVariants({
              variant: "default",
              className: "my-1",
            })
          )}
        >
          Create New Project
        </Link>
      </ActionContainer>
    </PageHeading>
  );
}
