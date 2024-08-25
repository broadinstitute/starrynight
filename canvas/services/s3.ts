import { getAWSCredentials } from "@/utils/localstorage";
import {
  GetObjectCommand,
  S3Client,
  PutObjectCommand,
} from "@aws-sdk/client-s3";

export type TFileType = "png" | "csv" | "tsv" | "xlsx" | "txt";

const getS3Client = ({
  projectId,
}: {
  projectId: string | number;
}): S3Client => {
  const cred = getAWSCredentials(projectId);

  console.log("Cred", cred, projectId);

  if (!cred) {
    throw new Error("No AWS credentials found for this project");
  }

  return new S3Client({
    region: cred.region,
    credentials: {
      accessKeyId: cred.accessKeyId,
      secretAccessKey: cred.secretAccessKey,
    },
  });
};

export type TGetKeyFileOptions = {
  toString?: {
    encoding?: "utf-8" | "base64";
  };
  projectId: string | number;
};

const getFile = async (url: string, options = {} as TGetKeyFileOptions) => {
  /**
   * Extract bucket and key from the url
   */
  const [Bucket, ...rest] = url.replace("s3://", "").split("/");
  const command = new GetObjectCommand({
    Bucket,
    Key: rest.join("/"),
  });

  const { toString, projectId } = options;
  const client = getS3Client({ projectId });

  try {
    const response = await client.send(command);

    const body =
      typeof toString?.encoding === "string"
        ? await response.Body?.transformToString(toString.encoding)
        : await response.Body?.transformToByteArray();
    return body;
  } catch (err) {
    console.log(err);
  }
};

export type TUpdateFileOptions = {
  ContentType: string;
  Body: string | Uint8Array | Buffer | File;
  projectId: string | number;
};

const uploadToS3 = async (url: string, options: TUpdateFileOptions) => {
  /**
   * Extract bucket and key from the url
   */
  const [Bucket, ...rest] = url.replace("s3://", "").split("/");

  const command = new PutObjectCommand({
    Bucket,
    Key: rest.join("/"),
    Body: options.Body,
    ContentType: options.ContentType,
  });

  const { projectId } = options;

  const client = getS3Client({ projectId });
  try {
    const response = await client.send(command);
    return response;
  } catch (err) {
    console.log(err);
  }
};

export { getS3Client, getFile, uploadToS3 };
