import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { normalizePayload, type ProductPayload, type ProductSchool } from "./school-utils";

let cachedPayload: ProductPayload | null = null;

export function loadProductPayload(): ProductPayload {
  if (cachedPayload) return cachedPayload;
  const payloadPath = resolve(process.cwd(), "public/data/site_payload.json");
  const raw = JSON.parse(readFileSync(payloadPath, "utf8"));
  cachedPayload = normalizePayload(raw);
  return cachedPayload;
}

export function loadSchools(): ProductSchool[] {
  return loadProductPayload().schools;
}

export function findSchool(slug: string): ProductSchool | undefined {
  return loadSchools().find((school) => school.slug === slug);
}
