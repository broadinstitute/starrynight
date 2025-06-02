import { Alert } from "@/components/custom/alert";
import { InputFormField } from "@/components/custom/form-field/input";
import { PageSpinner } from "@/components/custom/page-spinner";
import { Button } from "@/components/ui/button";
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
  projectId: string | number;
};

export function TakeCredentialsForm(props: TTakeCredentialsFormProps) {
  const { projectId } = props;
  const [isSaving, setIsSaving] = React.useState(false);
  const [showSuccessAlert, setShowSuccessAlert] = React.useState(false);

  const addAWSCredentialsForm = useForm<TAddAWSCredentials>({
    resolver: zodResolver(addAWSCredentials),
    defaultValues: getAWSCredentials(projectId),
  });

  const handleSavingAnimation = React.useCallback(() => {
    setTimeout(() => {
      setIsSaving(false);
      setShowSuccessAlert(true);

      setTimeout(() => {
        setShowSuccessAlert(false);
      }, 3000);
    }, 400);
  }, []);

  const handleOnFormSubmit = React.useCallback(
    (data: TAddAWSCredentials) => {
      setAWSCredentials(projectId, data);
      /**
       * After updating the credentials, we are resetting the form.
       */
      addAWSCredentialsForm.reset(getAWSCredentials(projectId));
      setIsSaving(true);
      handleSavingAnimation();
    },
    [projectId, addAWSCredentialsForm, handleSavingAnimation]
  );

  return (
    <Form {...addAWSCredentialsForm}>
      <form
        className="space-y-4 text-left max-w-xl"
        onSubmit={addAWSCredentialsForm.handleSubmit(handleOnFormSubmit)}
      >
        {showSuccessAlert && (
          <Alert
            variant="default"
            title="Success"
            description="AWS Credentials updated successfully."
          />
        )}
        <InputFormField
          control={addAWSCredentialsForm.control}
          name="accessKeyID"
          label="AWS Access Key ID"
          disabled={isSaving}
          inputProps={{
            placeholder: "AKIAIOSFODNN7EXAMPLE",
          }}
        />
        <InputFormField
          control={addAWSCredentialsForm.control}
          name="awsSecretKey"
          label="AWS Secret Key"
          disabled={isSaving}
          inputProps={{
            placeholder: "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
          }}
        />
        <InputFormField
          control={addAWSCredentialsForm.control}
          name="awsRegion"
          label="AWS Region"
          disabled={isSaving}
          inputProps={{
            placeholder: "us-west-1",
          }}
        />

        <div className="flex justify-end">
          <Button
            disabled={isSaving || !addAWSCredentialsForm.formState.isDirty}
          >
            {isSaving && <PageSpinner />}
            Save changes
          </Button>
        </div>
      </form>
    </Form>
  );
}
