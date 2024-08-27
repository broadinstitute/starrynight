"use client";

import { LazyLog, ScrollFollow } from "@melloware/react-logviewer";

export type TLogViewerProps = {
  endpoint: string;
};

export function LogViewer(props: TLogViewerProps) {
  const { endpoint } = props;
  let socket = null;

  return (
    <ScrollFollow
      startFollowing={true}
      render={({ follow, onScroll }) => (
        <LazyLog
          extraLines={1}
          enableSearch
          url={endpoint}
          websocket
          websocketOptions={{
            onOpen: (_e, sock) => {
              socket = sock;
              sock.send(JSON.stringify({ message: "Socket has been opened!" }));
            },
            formatMessage: (e) => JSON.parse(e).message,
            reconnect: true,
            reconnectWait: 5,
          }}
          onScroll={onScroll}
          follow={follow}
        />
      )}
    />
  );
}
