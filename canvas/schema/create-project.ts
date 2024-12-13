import { z } from "zod";

export const createProjectSchema = z.object({
  dataset: z.string(),
  parser: z.string(),
  type: z.string(),
  description: z.string().min(10).max(100),
  name: z.string().min(3).max(30),
  workspaceURI: z.string(),
});

export type TCreateProjectFormData = z.infer<typeof createProjectSchema>;
