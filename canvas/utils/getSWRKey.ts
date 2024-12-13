export function getStepSWRKey(projectId: string | number): string {
  return `/step/?project_id=${projectId}`;
}
