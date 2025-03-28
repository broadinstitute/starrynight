import { z } from "zod";

export const createProjectSchema = z.object({
  dataset: z.string(),
  parser: z.string(),
  type: z.string(),
  description: z.string().min(10).max(100),
  name: z.string().min(3).max(30),
  workspaceURI: z.string().optional(),
  storageURI: z.string().optional(),
  init_config: z.array(
    z.tuple([
      z.string(),
      z.string(),
      z.object({ title: z.string().optional() }),
    ])
  ),
});

export type TCreateProjectFormData = z.infer<typeof createProjectSchema>;
