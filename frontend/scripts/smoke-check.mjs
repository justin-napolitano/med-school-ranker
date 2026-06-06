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
const methodology = read("methodology/index.html");
const notInterested = read("not-interested/index.html");

if (!existsSync(dist)) {
  fail("Astro build output directory does not exist.");
}

if (!/<h1[^>]*>\s*Build My List\s*<\/h1>/i.test(index)) {
  fail("Build My List is not the first/product route heading.");
}

if (!index.includes("MCAT/GPA score-screen fit only; not acceptance probability")) {
  fail("Score-screen caveat is missing from the product route.");
}

if (!index.includes("Your Rank")) {
  fail("Build My List does not include Your Rank.");
}

if (!index.includes("Baseline Rank")) {
  fail("Build My List does not include Baseline Rank.");
}

if (!index.includes("shown /") || !index.includes("eligible /") || !index.includes("total")) {
  fail("Build My List does not expose shown / eligible / total counts.");
}

if (!notInterested.includes("<h1>Not Interested</h1>")) {
  fail("Not Interested route is missing.");
}

if (!methodology.includes("Live scoring formulas") || !methodology.includes("Missing values are never treated as zero")) {
  fail("Methodology does not document live scoring formulas and missing-data policy.");
}

if (index.includes("Data quality</span>") || index.includes("data-confidence filter") || index.includes("source-confidence filter")) {
  fail("Data-confidence/source-confidence filter control appears in Build My List output.");
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
  "likely admitted",
];
const unsupportedQualityClaims = [/public schools? (are|is) better/i, /private schools? (are|is) better/i, /public\/private quality/i, /higher-quality public/i, /higher-quality private/i];

for (const file of htmlFiles) {
  const text = readFileSync(file, "utf8").toLowerCase();
  for (const term of unsupportedZeroTolerance) {
    if (text.includes(term)) {
      fail(`Unsupported claim term "${term}" found in ${file}`);
    }
  }

  assertCaveated(text, file, "acceptance probability", /not\s+(a\s+|an\s+)?([\w-]+\s+){0,4}acceptance probability/);
  assertCaveated(text, file, "admit chance", /not\s+([\w-]+\s+){0,10}admit chance/);

  if (/>\s*hide\s*</i.test(text) || /hide school/i.test(text)) {
    fail(`Routine visible Hide control text found in ${file}`);
  }

  for (const pattern of unsupportedQualityClaims) {
    if (pattern.test(text)) {
      fail(`Unsupported public/private quality claim found in ${file}`);
    }
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

function assertCaveated(text, file, phrase, caveatPattern) {
  const phraseRegex = new RegExp(phrase, "g");
  for (const match of text.matchAll(phraseRegex)) {
    const index = match.index || 0;
    const context = text.slice(Math.max(0, index - 100), Math.min(text.length, index + 100));
    if (!caveatPattern.test(context)) {
      fail(`Uncaveated "${phrase}" language found in ${file}`);
      break;
    }
  }
}
