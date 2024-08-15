import Link from "next/link"
import { ArrowRightIcon } from "@radix-ui/react-icons"
import { Blocks } from "lucide-react"

import { Separator } from "@/src/components/ui/separator"

export function Announcement() {
  return (
    <Link
      href="#"
      className="inline-flex items-center rounded-lg bg-muted px-3 py-1 text-sm font-medium"
    >
      <Blocks className="h-4 w-4" />{" "}
      <Separator className="mx-2 h-4" orientation="vertical" />{" "}
      <span>Alpha release</span>
      {/* <ArrowRightIcon className="ml-1 h-4 w-4" /> */}
    </Link>
  )
}
