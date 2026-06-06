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
const applying = read("applying/index.html");
const compare = read("compare/index.html");
const interested = read("interested/index.html");
const methodology = read("methodology/index.html");
const notInterested = read("not-interested/index.html");
const recommendations = read("recommendations/index.html");
const scoring = read("scoring/index.html");
const schools = read("schools/index.html");
const schoolProfile = read("schools/nyu-grossman-long-island-school-of-medicine/index.html");
const deploymentBase = normalizeDeploymentBase(process.env.ASTRO_BASE_PATH);

if (!existsSync(dist)) {
  fail("Astro build output directory does not exist.");
}

if (!index.includes('data-app-shell="true"')) {
  fail("Index output does not include the React app shell.");
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

assertShellRoute(interested, "Interested", "50 school cap");
assertShellRoute(applying, "Applying", "25 school cap");
assertShellRoute(notInterested, "Not Interested", "removed from Build My List");
assertShellRoute(schools, "Schools", "Personal scoring override");

if (!schools.includes('data-app-route="schools"') || !schools.includes('data-school-browser="true"')) {
  fail("Schools route does not include the school-browser shell marker.");
}

if (!schools.includes("School directory") || !schools.includes("Global Score") || !schools.includes("Adjusted Score")) {
  fail("Schools route is missing directory scoring labels.");
}

if (!notInterested.includes("<h1>Not Interested</h1>")) {
  fail("Not Interested route is missing.");
}

if (!compare.includes('data-app-route="compare"') || !compare.includes("<h1>Compare</h1>") || !compare.includes("Add school")) {
  fail("Compare route does not include app-shell compare content.");
}

if (!methodology.includes("Live scoring formulas") || !methodology.includes("Missing values are never treated as zero")) {
  fail("Methodology does not document live scoring formulas and missing-data policy.");
}

if (!methodology.includes("/scoring/") || !methodology.includes("Zero-weight policy") || !methodology.includes("DO schools need a separate scoring flow")) {
  fail("Methodology does not link to Scoring or document zero-weight and DO-scope policy.");
}

if (!scoring.includes("<h1>Scoring</h1>")) {
  fail("Scoring route is missing.");
}

for (const requiredScoringText of [
  "Assumptions in use",
  "Weights and formulas",
  "School score breakdown",
  "present components only",
  "Why did this move?",
  "DO schools need a separate scoring flow",
  "Not included: weight is 0",
  "Your Rank",
  "Baseline Rank",
]) {
  if (!scoring.includes(requiredScoringText)) {
    fail(`Scoring route is missing required text: ${requiredScoringText}`);
  }
}

if (index.includes("Data quality</span>") || index.includes("data-confidence filter") || index.includes("source-confidence filter")) {
  fail("Data-confidence/source-confidence filter control appears in Build My List output.");
}

if (!schoolProfile.includes('data-app-route="school"') || !schoolProfile.includes("Score-screen Context") || !schoolProfile.includes("Why It Ranks Here")) {
  fail("School profile output does not include app-shell profile content.");
}

for (const profileAction of ["Interested", "Applying", "Not Interested", "Compare"]) {
  if (!schoolProfile.includes(profileAction)) {
    fail(`School profile output is missing local action text: ${profileAction}`);
  }
}

if (!schoolProfile.includes("Baseline Rank") || !schoolProfile.includes("Open source")) {
  fail("School profile output is missing baseline rank or source link content.");
}

if (!/data-surface="admin"/i.test(admin) || !/Admin\/Data/i.test(admin)) {
  fail("Admin route does not expose a distinct admin/data surface.");
}

if (admin.includes('data-app-shell="true"')) {
  fail("Admin route is rendering inside the applicant app shell.");
}

const applicantNav = extractShellNav(index);
if (!applicantNav) {
  fail("Applicant shell nav is missing from the product route.");
} else {
  if (!applicantNav.includes("Schools")) {
    fail("Schools is missing from the applicant shell nav.");
  }
  if (applicantNav.includes("Admin/Data")) {
    fail("Admin/Data appears as a normal applicant shell nav item.");
  }
  if (/Recommendations/i.test(applicantNav)) {
    fail("Recommendations appears as a normal applicant shell nav item.");
  }
}

if (!recommendations.includes("<h1>Build My List</h1>") || !recommendations.includes("previous Recommendations URL now opens Build My List")) {
  fail("Recommendations compatibility route does not alias to Build My List with deprecation text.");
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
  assertDeploymentBase(text, file, deploymentBase);

  for (const term of unsupportedZeroTolerance) {
    if (text.includes(term)) {
      fail(`Unsupported claim term "${term}" found in ${file}`);
    }
  }

  assertCaveated(text, file, "acceptance probability", /not\s+(a\s+|an\s+)?([\w-]+\s+){0,4}acceptance probability/);
  assertCaveated(text, file, "admissions probability", /not\s+(a\s+|an\s+)?([\w-]+\s+){0,4}admissions probability/);
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

function assertShellRoute(html, heading, requiredText) {
  if (!html.includes('data-app-shell="true"')) {
    fail(`${heading} route does not include the React app shell.`);
  }
  if (!new RegExp(`<h1[^>]*>\\s*${escapeRegExp(heading)}\\s*<\\/h1>`, "i").test(html)) {
    fail(`${heading} route is missing its shell heading.`);
  }
  if (!html.includes(requiredText)) {
    fail(`${heading} route is missing required text: ${requiredText}`);
  }
}

function extractShellNav(html) {
  return html.match(/<nav class="app-shell-nav"[\s\S]*?<\/nav>/i)?.[0] || "";
}

function normalizeDeploymentBase(value) {
  if (!value || value === "/") return "";
  const trimmed = value.trim().replace(/\/+$/, "");
  return trimmed.startsWith("/") ? trimmed : `/${trimmed}`;
}

function assertDeploymentBase(text, file, basePath) {
  if (!basePath) return;
  const baseSegment = escapeRegExp(basePath.slice(1));
  const unprefixedRootPath = new RegExp(`(?:href|src|component-url|renderer-url)="/(?!${baseSegment}(?:/|"))`, "i");
  if (unprefixedRootPath.test(text)) {
    fail(`Unprefixed root-relative link or asset found in ${file} for ASTRO_BASE_PATH=${basePath}`);
  }
}

function escapeRegExp(value) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}
