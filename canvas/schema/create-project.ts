import { z } from "zod";

export const createProjectSchema = z.object({
  dataset: z.string(),
  parser: z.string(),
});

export type TCreateProjectFormData = z.infer<typeof createProjectSchema>;
