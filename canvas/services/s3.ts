import { GetObjectCommand, S3Client } from "@aws-sdk/client-s3";

export type TFileType = "png" | "csv" | "tsv" | "xlsx" | "txt";

const getS3Client = (): S3Client => {
  return new S3Client({
    region: "us-east-1",
    signer: { sign: async (req) => req },
  });
};

export type TGetKeyFileOptions = {
  toString?: {
    encoding: "utf-8" | "base64";
  };
};

const getFile = async (Key: string, options = {} as TGetKeyFileOptions) => {
  const command = new GetObjectCommand({
    Bucket: process.env.NEXT_PUBLIC_BUCKET_NAME,
    Key,
  });

  const client = getS3Client();
  const { toString } = options;
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

export { getS3Client, getFile };
