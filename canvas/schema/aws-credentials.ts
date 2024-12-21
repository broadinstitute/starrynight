import { z } from "zod";

export const addAWSCredentials = z.object({
  accessKeyID: z
    .string()
    .min(16, "Access Key ID must be at least 16 characters long"),
  awsSecretKey: z
    .string()
    .min(40, "AWS Secret Key must be at least 40 characters long"),
  awsRegion: z.string().min(5, "AWS Region must be at least 5 characters long"),
});

export type TAddAWSCredentials = z.infer<typeof addAWSCredentials>;
