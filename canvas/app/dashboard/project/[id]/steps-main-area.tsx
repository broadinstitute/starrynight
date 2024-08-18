export type TStepContent = {
  title: string;
};

export type TStepMainAreaProps = {
  content: TStepContent;
};

export function StepsMainArea(props: TStepMainAreaProps) {
  const { content } = props;

  return (
    <div className="flex flex-col flex-1 overflow-auto">
      {content.title} <br />
    </div>
  );
}
