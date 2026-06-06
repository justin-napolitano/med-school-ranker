import { useCallback, useEffect, useMemo, useState } from "react";
import type { ReactNode } from "react";
import { appHref, appNavItems, isAdminPath, isApplicantShellPath, isExternalHref, normalizeAppPath, resolveAppRoute, type AppRoute } from "../lib/app-routing";
import type { ProductSchool } from "../lib/school-utils";
import { BuildMyListApp } from "./BuildMyListApp";
import { CompareApp } from "./CompareApp";
import { LocalListPage } from "./LocalListPage";
import { AppMethodologyView } from "./AppMethodologyView";
import { AppSchoolProfileView } from "./AppSchoolProfileView";
import { ScoringAssumptionsApp } from "./ScoringAssumptionsApp";
import { SchoolBrowserView } from "./SchoolBrowserView";
import { useLocalSchoolState, type LocalSchoolState } from "./useLocalSchoolState";

type ProductAppShellProps = {
  schools: ProductSchool[];
  caveat: string;
  aamcCaveat: string;
  methodology: Array<Record<string, any>>;
  initialPath: string;
};

type RouteHeader = {
  eyebrow: string;
  title: string;
  description: string;
  aside?: ReactNode;
};

export function ProductAppShell({ schools, caveat, aamcCaveat, methodology, initialPath }: ProductAppShellProps) {
  const local = useLocalSchoolState();
  const [currentPath, setCurrentPath] = useState(() => normalizeAppPath(initialPath || "/"));
  const route = useMemo(() => resolveAppRoute(currentPath), [currentPath]);
  const header = useMemo(() => buildRouteHeader(route, schools, caveat), [route, schools, caveat]);

  const navigateTo = useCallback((rawPath: string, mode: "push" | "replace" = "push") => {
    const nextPath = normalizeAppPath(rawPath);
    const nextRoute = resolveAppRoute(nextPath);
    if (nextRoute.kind === "notFound" || isAdminPath(nextPath)) return;

    const currentBrowserPath = normalizeAppPath(window.location.pathname);
    if (currentBrowserPath !== nextPath) {
      const nextHref = appHref(nextPath);
      if (mode === "replace") {
        window.history.replaceState({ appShell: true, path: nextPath }, "", nextHref);
      } else {
        window.history.pushState({ appShell: true, path: nextPath }, "", nextHref);
      }
    }

    setCurrentPath(nextPath);
    window.scrollTo({ top: 0, left: 0, behavior: "auto" });
  }, []);

  useEffect(() => {
    setCurrentPath(normalizeAppPath(window.location.pathname));
  }, []);

  useEffect(() => {
    function onPopState() {
      setCurrentPath(normalizeAppPath(window.location.pathname));
      window.scrollTo({ top: 0, left: 0, behavior: "auto" });
    }

    window.addEventListener("popstate", onPopState);
    return () => window.removeEventListener("popstate", onPopState);
  }, []);

  useEffect(() => {
    function onDocumentClick(event: MouseEvent) {
      if (event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
      if (!(event.target instanceof Element)) return;

      const anchor = event.target.closest("a") as HTMLAnchorElement | null;
      if (!anchor) return;
      if (anchor.getAttribute("target") || anchor.hasAttribute("download")) return;

      const rawHref = anchor.getAttribute("href") || "";
      if (!rawHref || rawHref.startsWith("#")) return;
      if (isExternalHref(anchor.href, window.location.origin)) return;

      let url: URL;
      try {
        url = new URL(anchor.href, window.location.href);
      } catch {
        return;
      }

      if (url.origin !== window.location.origin) return;
      if (url.hash && url.pathname === window.location.pathname && url.search === window.location.search) return;

      const nextPath = normalizeAppPath(url.pathname);
      if (isAdminPath(nextPath) || !isApplicantShellPath(nextPath)) return;

      event.preventDefault();
      navigateTo(nextPath);
    }

    document.addEventListener("click", onDocumentClick);
    return () => document.removeEventListener("click", onDocumentClick);
  }, [navigateTo]);

  return (
    <div className="product-app-shell" data-app-shell="true" data-app-route={route.kind}>
      <nav className="app-shell-nav" aria-label="Applicant workflow">
        {appNavItems.map((item) => (
          <a
            key={item.path}
            className={isNavActive(route, item.routeKind) ? "nav-link active" : "nav-link"}
            href={appHref(item.path)}
            aria-current={isNavActive(route, item.routeKind) ? "page" : undefined}
          >
            {item.label}
          </a>
        ))}
      </nav>

      <section className={route.kind === "school" ? "profile-header" : "page-header product-first"}>
        <div>
          <p className="eyebrow">{header.eyebrow}</p>
          <h1>{header.title}</h1>
          <p>{header.description}</p>
        </div>
        {header.aside}
      </section>

      {route.kind === "build" && route.deprecatedFrom ? (
        <p className="state-notice" role="status">
          The previous Recommendations URL now opens Build My List. Build My List is the canonical recommendation and list-building route.
        </p>
      ) : null}

      {renderRoute(route, schools, caveat, aamcCaveat, methodology, local)}
    </div>
  );
}

function renderRoute(
  route: AppRoute,
  schools: ProductSchool[],
  caveat: string,
  aamcCaveat: string,
  methodology: Array<Record<string, any>>,
  local: LocalSchoolState,
) {
  if (route.kind === "build") return <BuildMyListApp schools={schools} caveat={caveat} local={local} />;
  if (route.kind === "schools") return <SchoolBrowserView schools={schools} caveat={caveat} local={local} />;
  if (route.kind === "interested") return <LocalListPage schools={schools} caveat={caveat} listType="interested" local={local} />;
  if (route.kind === "applying") return <LocalListPage schools={schools} caveat={caveat} listType="applying" local={local} />;
  if (route.kind === "notInterested") return <LocalListPage schools={schools} caveat={caveat} listType="notInterested" local={local} />;
  if (route.kind === "compare") return <CompareApp schools={schools} caveat={caveat} local={local} />;
  if (route.kind === "scoring") return <ScoringAssumptionsApp schools={schools} caveat={caveat} local={local} />;
  if (route.kind === "methodology") return <AppMethodologyView caveat={caveat} aamcCaveat={aamcCaveat} methodology={methodology} />;
  if (route.kind === "school") return <AppSchoolProfileView schools={schools} slug={route.slug} caveat={caveat} local={local} />;

  return (
    <div className="empty-state">
      <h2>Route not found</h2>
      <p>This static applicant shell does not include that route.</p>
      <a className="action-link" href={appHref("/")}>
        Open Build My List
      </a>
    </div>
  );
}

function buildRouteHeader(route: AppRoute, schools: ProductSchool[], caveat: string): RouteHeader {
  if (route.kind === "interested") {
    return {
      eyebrow: "Shortlist",
      title: "Interested",
      description: `Browser-local list with a 50 school cap. ${caveat}`,
    };
  }
  if (route.kind === "schools") {
    return {
      eyebrow: "Directory",
      title: "Schools",
      description: `Browse the full school universe, open profiles, and apply optional browser-local scoring overrides. ${caveat}`,
    };
  }
  if (route.kind === "applying") {
    return {
      eyebrow: "Final list",
      title: "Applying",
      description: `Browser-local application list with a 25 school cap. ${caveat}`,
    };
  }
  if (route.kind === "notInterested") {
    return {
      eyebrow: "Removed from review",
      title: "Not Interested",
      description: `Browser-local list of schools removed from Build My List. ${caveat}`,
    };
  }
  if (route.kind === "compare") {
    return {
      eyebrow: "Selected schools",
      title: "Compare",
      description: caveat,
    };
  }
  if (route.kind === "scoring") {
    return {
      eyebrow: "Score audit",
      title: "Scoring",
      description: `${caveat} This Scoring page covers MD schools only. DO schools need a separate scoring flow because the source context and applicant-pool assumptions differ.`,
    };
  }
  if (route.kind === "methodology") {
    return {
      eyebrow: "Transparent scoring",
      title: "Methodology",
      description: "The app uses generated deterministic data and browser-local preferences. It does not run a predictive admissions model.",
    };
  }
  if (route.kind === "school") {
    const school = schools.find((item) => item.slug === route.slug);
    if (!school) {
      return {
        eyebrow: "School profile",
        title: "Profile not found",
        description: "This static build does not include that school profile.",
      };
    }
    return {
      eyebrow: `${school.degree || "Degree not listed"} / ${school.city || "City not listed"}, ${school.stateAbbrev || school.state || "State not listed"}`,
      title: school.name,
      description: caveat,
      aside: (
        <div className="rank-pill large">
          <span>{school.rankLabel || "Baseline Rank"}</span>
          <strong>{school.decisionRank ? `#${school.decisionRank}` : "Unranked"}</strong>
        </div>
      ),
    };
  }
  if (route.kind === "notFound") {
    return {
      eyebrow: "Static route",
      title: "Route not found",
      description: "This applicant shell route is not part of the static product build.",
    };
  }
  return {
    eyebrow: "First pass",
    title: "Build My List",
    description: caveat,
  };
}

function isNavActive(route: AppRoute, routeKind: AppRoute["kind"]): boolean {
  if (route.kind === "build" && routeKind === "build") return true;
  return route.kind === routeKind;
}
