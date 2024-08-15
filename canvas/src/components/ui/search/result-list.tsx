"use client";

export type TResultListProps = {
  /**
   * The list of results to display.
   */
  results: { readonly objectID: string; project_id?: string }[];
};

export default function ResultList(props: TResultListProps) {
  const { results } = props;

  return (
    <div className="mt-4">
      {results.map((result) => (
        <div
          className="p-4 border my-2  rounded hover:bg-slate-100"
          key={result.objectID}
        >
          Project: {result.project_id}
        </div>
      ))}
    </div>
  );
}
