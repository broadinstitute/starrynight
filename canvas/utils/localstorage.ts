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

export type TAWSCredentials = {
  accessKeyId: string;
  secretAccessKey: string;
  region: string;
};

export const getAWSCredentials = (
  projectId: string | number
): TAWSCredentials | null => {
  const key = `aws-credentials-${projectId}`;
  const value = getLocalStorageValue(key);

  if (typeof value !== "string" || !value) {
    return null;
  }

  try {
    const parsedValue = JSON.parse(value) as unknown;

    if (typeof parsedValue !== "object" || !parsedValue) {
      return null;
    }

    if (
      "accessKeyId" in parsedValue &&
      "secretAccessKey" in parsedValue &&
      "region" in parsedValue
    ) {
      return parsedValue as TAWSCredentials;
    }

    return null;
  } catch (e) {
    console.error("Error parsing localStorage value", e);
    return null;
  }
};

export const setAWSCredentials = (
  projectId: string | number,
  value: TAWSCredentials
) => {
  const key = `aws-credentials-${projectId}`;
  try {
    setLocalStorageValue(key, JSON.stringify(value)) || "";
  } catch (error) {
    console.log("Error setting AWS credentials", error);
  }
};
