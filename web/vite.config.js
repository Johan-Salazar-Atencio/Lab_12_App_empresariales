import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

// The dev server runs on 5173: this is the origin that the API authorizes with CORS.
export default defineConfig({
  plugins: [react()],
  server: { port: 5173, strictPort: true },
});
