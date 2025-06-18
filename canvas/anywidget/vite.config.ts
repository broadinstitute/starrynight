import { defineConfig } from "vite";
import path from "path";
import anywidget from "@anywidget/vite";

// https://vite.dev/config/
export default defineConfig({
  build: {
    outDir: "dist",
    lib: {
      entry: ["src/App.tsx"],
      formats: ["es"],
    },
  },
  define: {
    "process.env.NODE_ENV": '"production"',
  },
  plugins: [anywidget()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
});
