/** @type {import('next').NextConfig} */
import path from "path";

const nextConfig = {
  transpilePackages: ["@duckdb/react-duckdb"],

  webpack: (config, { isServer }) => {
    config.experiments = {
      asyncWebAssembly: true,
      layers: true,
    };

    config.module.rules.push({
      test: /\.wasm$/,
      type: "asset/resource",
      generator: {
        filename: "static/wasm/[name].[contenthash][ext]",
      },
    });

    config.module.rules.push({
      test: /\.(parquet)$/i,
      type: "asset/resource",
      generator: {
        filename: "static/parquet/[name].[contenthash][ext]",
      },
    });

    config.module.rules.push({
      test: /\.(sql)$/i,
      type: "asset/resource",
      generator: {
        filename: "static/scripts/[name].[contenthash][ext]",
      },
    });

    return config;
  },
};

export default nextConfig;
