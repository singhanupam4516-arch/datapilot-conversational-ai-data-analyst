import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Plain JS config — no TypeScript, no Tailwind plugin. @vitejs/plugin-react
// turns JSX into plain JS; that is all the tooling this project uses.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
  },
});
