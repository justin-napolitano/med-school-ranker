#!/usr/bin/env node
import { copyFileSync, existsSync, mkdirSync, readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const scriptDir = dirname(fileURLToPath(import.meta.url));
const frontendRoot = resolve(scriptDir, "..");
const repoRoot = resolve(frontendRoot, "..");
const source = resolve(repoRoot, "outputs/site/data/site_payload.json");
const destination = resolve(frontendRoot, "public/data/site_payload.json");

if (!existsSync(source)) {
  console.error(`Missing generated payload: ${source}`);
  console.error("Run: uv run med-school-build-site --site-mode publish_safe");
  process.exit(1);
}

const payload = JSON.parse(readFileSync(source, "utf8"));
if (!payload?.schools?.length) {
  console.error("Generated payload does not contain schools.");
  process.exit(1);
}

mkdirSync(dirname(destination), { recursive: true });
copyFileSync(source, destination);
console.log(`Copied ${payload.schools.length} schools to ${destination}`);
