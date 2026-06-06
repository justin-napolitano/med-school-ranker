import { withBase } from "./site-url";

export type AppRoute =
  | { kind: "build"; deprecatedFrom?: "/recommendations/" }
  | { kind: "schools" }
  | { kind: "interested" }
  | { kind: "applying" }
  | { kind: "notInterested" }
  | { kind: "compare" }
  | { kind: "scoring" }
  | { kind: "methodology" }
  | { kind: "school"; slug: string }
  | { kind: "notFound"; path: string };

export type AppNavItem = {
  path: string;
  label: string;
  routeKind: Exclude<AppRoute["kind"], "school" | "notFound">;
};

export const appNavItems: AppNavItem[] = [
  { path: "/", label: "Build My List", routeKind: "build" },
  { path: "/schools/", label: "Schools", routeKind: "schools" },
  { path: "/interested/", label: "Interested", routeKind: "interested" },
  { path: "/applying/", label: "Applying", routeKind: "applying" },
  { path: "/not-interested/", label: "Not Interested", routeKind: "notInterested" },
  { path: "/compare/", label: "Compare", routeKind: "compare" },
  { path: "/scoring/", label: "Scoring", routeKind: "scoring" },
  { path: "/methodology/", label: "Methodology", routeKind: "methodology" },
];

export function appHref(path: string): string {
  return withBase(normalizeAppPath(path));
}

export function normalizeAppPath(value: string): string {
  const pathname = extractPathname(value);
  const withoutBase = stripBasePath(pathname);
  return ensureTrailingSlash(withoutBase);
}

export function resolveAppRoute(value: string): AppRoute {
  const path = normalizeAppPath(value);
  if (path === "/") return { kind: "build" };
  if (path === "/recommendations/") return { kind: "build", deprecatedFrom: "/recommendations/" };
  if (path === "/schools/") return { kind: "schools" };
  if (path === "/interested/") return { kind: "interested" };
  if (path === "/applying/") return { kind: "applying" };
  if (path === "/not-interested/") return { kind: "notInterested" };
  if (path === "/compare/") return { kind: "compare" };
  if (path === "/scoring/") return { kind: "scoring" };
  if (path === "/methodology/") return { kind: "methodology" };

  const schoolMatch = path.match(/^\/schools\/([^/]+)\/$/);
  if (schoolMatch) return { kind: "school", slug: decodeURIComponent(schoolMatch[1]) };

  return { kind: "notFound", path };
}

export function isAdminPath(value: string): boolean {
  return normalizeAppPath(value).startsWith("/admin/");
}

export function isApplicantShellPath(value: string): boolean {
  const route = resolveAppRoute(value);
  return route.kind !== "notFound" && !isAdminPath(value);
}

export function isExternalHref(href: string, currentOrigin = "https://app.local"): boolean {
  if (!href || href.startsWith("#")) return false;
  try {
    const url = new URL(href, currentOrigin);
    if (url.protocol !== "http:" && url.protocol !== "https:") return true;
    return url.origin !== currentOrigin;
  } catch {
    return false;
  }
}

function extractPathname(value: string): string {
  if (!value) return "/";
  if (value.startsWith("#")) return "/";

  try {
    const url = new URL(value, "https://app.local");
    return url.pathname || "/";
  } catch {
    return value.split(/[?#]/)[0] || "/";
  }
}

function stripBasePath(pathname: string): string {
  const basePath = currentBasePath();
  if (!basePath) return pathname || "/";
  if (pathname === basePath) return "/";
  if (pathname.startsWith(`${basePath}/`)) return pathname.slice(basePath.length) || "/";
  return pathname || "/";
}

function currentBasePath(): string {
  const rawBase = import.meta.env.BASE_URL || "/";
  const trimmed = rawBase.trim().replace(/\/+$/, "");
  return trimmed === "/" ? "" : trimmed;
}

function ensureTrailingSlash(path: string): string {
  const normalized = path.startsWith("/") ? path : `/${path}`;
  if (normalized === "/") return normalized;
  return normalized.endsWith("/") ? normalized : `${normalized}/`;
}
