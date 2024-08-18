export type TPageHeadingProps = {
  /**
   * If defined then heading will be shown.
   */
  heading?: string;
  primaryAction?: React.ReactNode;
};

export function PageHeading(props: TPageHeadingProps) {
  const { heading, primaryAction } = props;

  return (
    <div className="flex mt-3 flex-col pb-8 md:flex-row md:justify-between md:items-center md:mt-6 md:border-b md:border-b-slate-200">
      <div className="font-thin text-5xl mb-8 md:mb-0">{heading}</div>
      {primaryAction}
    </div>
  );
}
