export type TSpecPathRecord = {
  name: string;
  type: "files" | "notebook";
  description: string;
  optional: boolean;
  path: string;
  format: [string];
  collection: boolean;
  subtype: [string];
  z: boolean;
  t: boolean;
  tiled: boolean;
  pyramidal: boolean;
  value: string;
};
