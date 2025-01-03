export type TFileViewerMessageProps = {
  message: string;
};

export function FileViewerMessage(props: TFileViewerMessageProps) {
  const { message } = props;

  return (
    <div className="flex flex-1 p-4 items-center justify-center text-gray-500">
      {message}
    </div>
  );
}
