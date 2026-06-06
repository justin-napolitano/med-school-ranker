#!/usr/bin/env node
import { existsSync, readdirSync, readFileSync, statSync } from "node:fs";
import { join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const frontendRoot = resolve(fileURLToPath(new URL("..", import.meta.url)));
const dist = resolve(frontendRoot, "dist");
const failures = [];

function fail(message) {
  failures.push(message);
}

function read(relativePath) {
  const path = join(dist, relativePath);
  if (!existsSync(path)) {
    fail(`Missing build artifact: ${relativePath}`);
    return "";
  }
  return readFileSync(path, "utf8");
}

function walkHtml(dir) {
  if (!existsSync(dir)) return [];
  const entries = readdirSync(dir);
  const files = [];
  for (const entry of entries) {
    const path = join(dir, entry);
    const stats = statSync(path);
    if (stats.isDirectory()) {
      files.push(...walkHtml(path));
    } else if (entry.endsWith(".html")) {
      files.push(path);
    }
  }
  return files;
}

const index = read("index.html");
const admin = read("admin/index.html");

if (!existsSync(dist)) {
  fail("Astro build output directory does not exist.");
}

if (!/<h1[^>]*>\s*Build My List\s*<\/h1>/i.test(index)) {
  fail("Build My List is not the first/product route heading.");
}

if (!index.includes("MCAT/GPA score-screen fit only; not acceptance probability")) {
  fail("Score-screen caveat is missing from the product route.");
}

if (!/data-surface="admin"/i.test(admin) || !/Admin\/Data/i.test(admin)) {
  fail("Admin route does not expose a distinct admin/data surface.");
}

const htmlFiles = walkHtml(dist);
const unsupportedZeroTolerance = [
  "guaranteed admission",
  "best school",
  "safe school",
  "sure thing",
];

for (const file of htmlFiles) {
  const text = readFileSync(file, "utf8").toLowerCase();
  for (const term of unsupportedZeroTolerance) {
    if (text.includes(term)) {
      fail(`Unsupported claim term "${term}" found in ${file}`);
    }
  }

  const probabilityRegex = /acceptance probability/g;
  for (const match of text.matchAll(probabilityRegex)) {
    const index = match.index || 0;
    const context = text.slice(Math.max(0, index - 80), Math.min(text.length, index + 80));
    if (!/not\s+(a\s+|an\s+)?([\w-]+\s+){0,4}acceptance probability/.test(context)) {
      fail(`Uncaveated "acceptance probability" language found in ${file}`);
      break;
    }
  }

  if (/>\s*hide\s*</i.test(text) || /hide school/i.test(text)) {
    fail(`Routine visible Hide control text found in ${file}`);
  }
}

if (failures.length) {
  console.error("Smoke check failed:");
  for (const failure of failures) {
    console.error(`- ${failure}`);
  }
  process.exit(1);
}

console.log(`Smoke check passed across ${htmlFiles.length} HTML files.`);
