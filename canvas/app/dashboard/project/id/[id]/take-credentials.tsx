import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import {
  getAWSCredentials,
  setAWSCredentials,
  TAWSCredentials,
} from "@/utils/localstorage";
import { Label } from "@radix-ui/react-label";
import { Settings } from "lucide-react";
import React from "react";

export type TTakeCredentialsProps = {
  projectId: string | number;
};

export function TakeCredentials(props: TTakeCredentialsProps) {
  const { projectId } = props;
  const [credentials, setCredentials] = React.useState(
    getAWSCredentials(projectId) || {
      accessKeyId: "",
      secretAccessKey: "",
      region: "",
    }
  );

  function handleOnAddClick() {
    const { accessKeyId, secretAccessKey, region } = credentials;

    if (!accessKeyId || !secretAccessKey || !region) {
      console.error("Please fill all the fields");
      return;
    }

    setAWSCredentials(projectId, { accessKeyId, secretAccessKey, region });
  }

  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button variant="outline">
          <Settings className="mr-2 h-4 w-4" />
          Add AWS credentials
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Add AWS Credentials</DialogTitle>
        </DialogHeader>
        <div className="space-y-4">
          <div className="space-y-2">
            <Label>AWS access key id</Label>
            <Input
              value={credentials.accessKeyId}
              onChange={(e) =>
                setCredentials({
                  ...credentials,
                  accessKeyId: e.currentTarget.value,
                })
              }
              placeholder="AWS access key id"
            />
          </div>
          <div className="space-y-2">
            <Label>AWS secret access key</Label>
            <Input
              value={credentials.secretAccessKey}
              onChange={(e) =>
                setCredentials({
                  ...credentials,
                  secretAccessKey: e.currentTarget.value,
                })
              }
              placeholder="AWS secret access key"
            />
          </div>
          <div className="space-y-2">
            <Label>AWS Region</Label>
            <Input
              value={credentials.region}
              onChange={(e) =>
                setCredentials({
                  ...credentials,
                  region: e.currentTarget.value,
                })
              }
              placeholder="AWS region"
            />
          </div>
        </div>
        <DialogFooter>
          <DialogClose asChild>
            <Button onClick={handleOnAddClick}>Add credentials</Button>
          </DialogClose>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
