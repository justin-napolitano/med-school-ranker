import { defineConfig } from "astro/config";
import react from "@astrojs/react";

const base = process.env.ASTRO_BASE_PATH || "/";
const site = process.env.ASTRO_SITE_URL;

export default defineConfig({
  base,
  site,
  output: "static",
  integrations: [react()],
});
