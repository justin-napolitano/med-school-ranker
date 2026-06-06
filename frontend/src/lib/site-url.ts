const rawBase = import.meta.env.BASE_URL || "/";
const basePath = rawBase.endsWith("/") ? rawBase.slice(0, -1) : rawBase;

export function withBase(path: string): string {
  if (!path) return basePath || "/";
  if (/^[a-z][a-z0-9+.-]*:/i.test(path) || path.startsWith("#")) return path;

  const normalizedPath = path.startsWith("/") ? path : `/${path}`;
  if (!basePath) return normalizedPath;
  if (normalizedPath === basePath || normalizedPath.startsWith(`${basePath}/`)) return normalizedPath;
  return `${basePath}${normalizedPath}`;
}
