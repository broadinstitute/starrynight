"use client";

import * as React from "react";
import dynamic from "next/dynamic";

import * as duckdb from "@duckdb/duckdb-wasm";
import duckdb_wasm from "@duckdb/duckdb-wasm/dist/duckdb-mvp.wasm";
import duckdb_wasm_eh from "@duckdb/duckdb-wasm/dist/duckdb-eh.wasm";
import duckdb_wasm_coi from "@duckdb/duckdb-wasm/dist/duckdb-coi.wasm";

// import "bootstrap/dist/css/bootstrap.min.css";
import "xterm/css/xterm.css";

import {
  DuckDBConnectionProvider,
  DuckDBPlatform,
  DuckDBProvider,
} from "@duckdb/react-duckdb";

const Shell = dynamic((
  () => import("./shell")
), { ssr: false })

const DUCKDB_BUNDLES: duckdb.DuckDBBundles = {
  mvp: {
    mainModule: duckdb_wasm,
    mainWorker: "/duckdb-wasm/duckdb-browser-mvp.worker.js",
  },
  eh: {
    mainModule: duckdb_wasm_eh,
    mainWorker: "/duckdb-wasm/duckdb-browser-eh.worker.js",
  },
  coi: {
    mainModule: duckdb_wasm_coi,
    mainWorker: "/duckdb-wasm/duckdb-browser-coi.worker.js",
    pthreadWorker: "/duckdb-wasm/duckdb-browser-coi.pthread.worker.js",
  },
};

const logger = new duckdb.ConsoleLogger(duckdb.LogLevel.WARNING);

const DuckApp: React.FC = () => {
  return (
    <DuckDBPlatform logger={logger} bundles={DUCKDB_BUNDLES}>
      <DuckDBProvider>
        <DuckDBConnectionProvider>
          <Shell padding={[16, 0, 0, 20]} backgroundColor="#333" />
        </DuckDBConnectionProvider>
      </DuckDBProvider>
    </DuckDBPlatform>
  );
}

export default DuckApp;
