import { PROJECTS_LISTING_URL } from "@/constants/routes";
import { redirect } from "next/navigation";

export default function Page() {
  // Redirecting users to project listing page.
  redirect(PROJECTS_LISTING_URL);

  return <div className="p-2">Loading..</div>;
}
