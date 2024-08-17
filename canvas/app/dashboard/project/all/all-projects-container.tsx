export function AllProjectContainer(props: React.PropsWithChildren) {
  const { children } = props;
  return <div className="py-4 flex flex-wrap gap-8 md:py-8">{children}</div>;
}
