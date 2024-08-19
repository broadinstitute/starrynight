import { Badge } from "@/components/ui/badge";

export type TJobBadgeProps = {
  status: string;
};

export function JobBadge(props: TJobBadgeProps) {
  const { status } = props;

  if (status === "pending") {
    return <Badge variant="outline">Pending</Badge>;
  }
  if (status === "running") {
    return <Badge variant="secondary">Running</Badge>;
  }
  if (status === "success") {
    return <Badge variant="default">Success</Badge>;
  }
  if (status === "failed") {
    return <Badge variant="destructive">Failed</Badge>;
  }

  return null;
}
