import { InputFormField } from "@/components/custom/form-field/input";
import { Form } from "@/components/ui/form";
import {
  addAWSCredentials,
  TAddAWSCredentials,
} from "@/schema/aws-credentials";
import { getAWSCredentials, setAWSCredentials } from "@/utils/localstorage";
import { zodResolver } from "@hookform/resolvers/zod";
import React from "react";
import { useForm } from "react-hook-form";

export type TTakeCredentialsFormProps = {
  formId: string;
  projectId: string | number;
  onRequestClose: () => void;
};

export function TakeCredentialsForm(props: TTakeCredentialsFormProps) {
  const { formId, projectId, onRequestClose } = props;

  const addAWSCredentialsForm = useForm<TAddAWSCredentials>({
    resolver: zodResolver(addAWSCredentials),
    defaultValues: getAWSCredentials(projectId),
  });

  const handleOnFormSubmit = React.useCallback(
    (data: TAddAWSCredentials) => {
      setAWSCredentials(projectId, data);
      onRequestClose();
    },
    [onRequestClose, projectId]
  );

  return (
    <Form {...addAWSCredentialsForm}>
      <form
        className="space-y-4 text-left"
        id={formId}
        onSubmit={addAWSCredentialsForm.handleSubmit(handleOnFormSubmit)}
      >
        <InputFormField
          control={addAWSCredentialsForm.control}
          name="accessKeyID"
          label="AWS Access Key ID"
          inputProps={{
            placeholder: "AKIAIOSFODNN7EXAMPLE",
          }}
        />
        <InputFormField
          control={addAWSCredentialsForm.control}
          name="awsSecretKey"
          label="AWS Secret Key"
          inputProps={{
            placeholder: "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
          }}
        />
        <InputFormField
          control={addAWSCredentialsForm.control}
          name="awsRegion"
          label="AWS Region"
          inputProps={{
            placeholder: "us-west-1",
          }}
        />
      </form>
    </Form>
  );
}
