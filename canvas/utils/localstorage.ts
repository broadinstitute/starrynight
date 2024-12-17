import {
  addAWSCredentials,
  TAddAWSCredentials,
} from "@/schema/aws-credentials";

/**
 * To return the value using key from the localStorage.
 */
export const getLocalStorageValue = (key: string): unknown => {
  if (typeof window === "undefined") {
    return null;
  }

  if (!localStorage.getItem(key)) {
    return null;
  }
  try {
    return JSON.parse(localStorage.getItem(key)!);
  } catch (e) {
    console.error("Error parsing localStorage value", e);
    return null;
  }
};

/**
 * To store the value in the localStorage using key.
 */
export const setLocalStorageValue = (key: string, value: unknown) => {
  if (typeof window === "undefined") {
    return false;
  }

  try {
    localStorage.setItem(key, JSON.stringify(value));
    return true;
  } catch (e) {
    console.error("Error setting localStorage value", e);
    return false;
  }
};

const DEFAULT_AWS_CRED: TAddAWSCredentials = {
  accessKeyID: "",
  awsRegion: "",
  awsSecretKey: "",
};

export const getAWSCredentials = (
  projectId: string | number
): TAddAWSCredentials => {
  const key = `aws-credentials-${projectId}`;
  const value = getLocalStorageValue(key);

  if (typeof value !== "string" || !value) {
    return DEFAULT_AWS_CRED;
  }

  try {
    const parsedValue = JSON.parse(value) as unknown;

    if (typeof parsedValue !== "object" || !parsedValue) {
      return DEFAULT_AWS_CRED;
    }

    if (addAWSCredentials.safeParse(parsedValue)) {
      return parsedValue as TAddAWSCredentials;
    }

    return DEFAULT_AWS_CRED;
  } catch (e) {
    console.error("Error parsing localStorage value", e);
    return DEFAULT_AWS_CRED;
  }
};

export const setAWSCredentials = (
  projectId: string | number,
  value: TAddAWSCredentials
) => {
  const key = `aws-credentials-${projectId}`;
  try {
    setLocalStorageValue(key, JSON.stringify(value)) || "";
  } catch (error) {
    console.log("Error setting AWS credentials", error);
  }
};
