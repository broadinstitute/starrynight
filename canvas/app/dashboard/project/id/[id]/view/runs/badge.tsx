import { Badge } from "@/components/ui/badge";

export type TProjectRunBadge = {
  status: string;
};

export function ProjectRunBadge(props: TProjectRunBadge) {
  const { status } = props;

  if (status === "pending") {
    return <Badge variant="default">Pending</Badge>;
  }
  if (status === "running") {
    return <Badge variant="info">Running</Badge>;
  }
  if (status === "success") {
    return <Badge variant="success">Success</Badge>;
  }
  if (status === "failed") {
    return <Badge variant="destructive">Failed</Badge>;
  }

  return null;
}
