import { defineConfig } from "vite";
import pkg from "@remix-run/dev";
const { vitePlugin: remix } = pkg as unknown as {
  vitePlugin: (opts?: any) => any;
};

export default defineConfig({
  plugins: [remix()],
  server: {
    host: true,
    port: 5174,
  },
  ssr: {
    noExternal: [/^@mui\//, /^@emotion\//],
  },
  optimizeDeps: {
    include: [
      "@mui/material",
      "@mui/icons-material",
      "@emotion/react",
      "@emotion/styled",
    ],
  },
});
