"use client";

import { useDimension } from "@/hooks/useDimension";
import { LazyLog, ScrollFollow } from "@melloware/react-logviewer";
import React from "react";
import { PageSpinner } from "./page-spinner";

export type TLogViewerProps = {
  endpoint: string;
};

export function LogViewer(props: TLogViewerProps) {
  const { endpoint } = props;
  const ref = React.useRef<HTMLDivElement>(null);

  const { width, height } = useDimension({ ref });

  return (
    <div ref={ref} className="flex-1">
      {width === 0 || height === 0 ? (
        <PageSpinner />
      ) : (
        /**
         * ScrollFollow wrapper should have a parent with a fixed width and height.
         * @link https://github.com/melloware/react-logviewer?tab=readme-ov-file#usage-1
         */
        <div style={{ width, height }}>
          <ScrollFollow
            startFollowing={true}
            render={({ follow, onScroll }) => (
              <LazyLog
                extraLines={1}
                enableSearch
                url={endpoint}
                websocket
                websocketOptions={{
                  reconnect: true,
                  reconnectWait: 5,
                  formatMessage: (e) => JSON.parse(e).message
                }}
                onScroll={onScroll}
                follow={follow}
              />
            )}
          />
        </div>
      )}
    </div>
  );
}
