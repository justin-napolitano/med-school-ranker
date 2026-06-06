import { ArrowUpRight, ClipboardCheck, Download, MinusCircle, RotateCcw, Scale, SlidersHorizontal, Star } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { formatLiveScore, formatRank, scoreSchoolsWithOverrides, type SchoolAdjustedScore } from "../lib/live-scoring";
import type { ProductSchool } from "../lib/school-utils";
import { formatCurrency, metricValue, stateLabel, statesForSchools } from "../lib/school-utils";
import { SchoolOverrideEditor } from "./SchoolOverrideEditor";
import type { LocalSchoolState } from "./useLocalSchoolState";

type SchoolBrowserViewProps = {
  schools: ProductSchool[];
  caveat: string;
  local: LocalSchoolState;
};

type DegreeFilter = "all" | "MD" | "DO";
type StatusFilter = "all" | "none" | "interested" | "applying" | "notInterested" | "compared";
type OverrideFilter = "all" | "applied" | "none";
type SortKey = "global-rank" | "name" | "global-score" | "adjusted-score";

const INITIAL_VISIBLE_COUNT = 60;

export function SchoolBrowserView({ schools, caveat, local }: SchoolBrowserViewProps) {
  const [query, setQuery] = useState("");
  const [degree, setDegree] = useState<DegreeFilter>("all");
  const [state, setState] = useState("all");
  const [status, setStatus] = useState<StatusFilter>("all");
  const [overrideFilter, setOverrideFilter] = useState<OverrideFilter>("all");
  const [sort, setSort] = useState<SortKey>("global-rank");
  const [visibleLimit, setVisibleLimit] = useState(INITIAL_VISIBLE_COUNT);
  const [editingSlug, setEditingSlug] = useState("");
  const stateOptions = useMemo(() => statesForSchools(schools), [schools]);
  const scoreRows = useMemo(
    () => scoreSchoolsWithOverrides(schools, local.preferences, local.schoolWeightOverrides),
    [schools, local.preferences, local.schoolWeightOverrides],
  );
  const visibleRows = useMemo(
    () =>
      scoreRows
        .filter((row) => matchesSearch(row, query))
        .filter((row) => degree === "all" || row.globalScore.school.degree === degree)
        .filter((row) => state === "all" || row.globalScore.school.stateAbbrev === state)
        .filter((row) => matchesStatus(row, status, local))
        .filter((row) => overrideFilter === "all" || (overrideFilter === "applied" ? row.overrideApplied : !row.overrideApplied))
        .sort((a, b) => compareBrowserRows(a, b, sort)),
    [degree, local, overrideFilter, query, scoreRows, sort, state, status],
  );
  const shownRows = visibleRows.slice(0, visibleLimit);
  const overrideCount = Object.keys(local.schoolWeightOverrides).length;
  const remainingCount = Math.max(visibleRows.length - shownRows.length, 0);

  useEffect(() => {
    setVisibleLimit(INITIAL_VISIBLE_COUNT);
  }, [degree, overrideFilter, query, sort, state, status]);

  function resetFilters() {
    setQuery("");
    setDegree("all");
    setState("all");
    setStatus("all");
    setOverrideFilter("all");
    setSort("global-rank");
  }

  function clearAllOverrides() {
    if (!overrideCount) return;
    if (window.confirm(`Reset all ${overrideCount} school-specific scoring overrides?`)) {
      local.clearSchoolWeightOverrides();
      setEditingSlug("");
    }
  }

  function exportOverrides() {
    const rows = Object.values(local.schoolWeightOverrides);
    if (!rows.length) return;
    const schoolBySlug = new Map(schools.map((school) => [school.slug, school]));
    const csvRows = [
      ["school_slug", "school_name", "mcat_weight", "gpa_weight", "state_weight", "cost_weight", "context_weight", "updated_at"],
      ...rows.map((override) => {
        const school = schoolBySlug.get(override.schoolSlug);
        return [
          override.schoolSlug,
          school?.name || "",
          String(override.weights.mcatFit ?? ""),
          String(override.weights.gpaFit ?? ""),
          String(override.weights.stateFit ?? ""),
          String(override.weights.costFit ?? ""),
          String(override.weights.baselineAttendance ?? ""),
          override.updatedAt,
        ];
      }),
    ];
    const blob = new Blob([csvRows.map((row) => row.map(csvCell).join(",")).join("\n")], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "school-weight-overrides.csv";
    link.click();
    URL.revokeObjectURL(url);
  }

  return (
    <div className="school-browser-surface" data-school-browser="true">
      <aside className="builder-panel school-browser-controls" aria-label="School browser filters">
        <div className="panel-heading">
          <p className="eyebrow">Directory tools</p>
          <h2>Find schools</h2>
        </div>

        <div className="control-grid">
          <label className="wide">
            <span>Search</span>
            <input value={query} onChange={(event) => setQuery(event.currentTarget.value)} placeholder="School, city, or state" />
          </label>
          <label>
            <span>Degree</span>
            <select value={degree} onChange={(event) => setDegree(event.currentTarget.value as DegreeFilter)}>
              <option value="all">All degrees</option>
              <option value="MD">MD</option>
              <option value="DO">DO</option>
            </select>
          </label>
          <label>
            <span>State</span>
            <select value={state} onChange={(event) => setState(event.currentTarget.value)}>
              <option value="all">All states</option>
              {stateOptions.map((stateOption) => (
                <option value={stateOption} key={stateOption}>
                  {stateLabel(stateOption)}
                </option>
              ))}
            </select>
          </label>
          <label>
            <span>Status</span>
            <select value={status} onChange={(event) => setStatus(event.currentTarget.value as StatusFilter)}>
              <option value="all">All statuses</option>
              <option value="none">None</option>
              <option value="interested">Interested</option>
              <option value="applying">Applying</option>
              <option value="notInterested">Not Interested</option>
              <option value="compared">Compared</option>
            </select>
          </label>
          <label>
            <span>Override</span>
            <select value={overrideFilter} onChange={(event) => setOverrideFilter(event.currentTarget.value as OverrideFilter)}>
              <option value="all">All schools</option>
              <option value="applied">Override applied</option>
              <option value="none">No override</option>
            </select>
          </label>
          <label className="wide">
            <span>Sort</span>
            <select value={sort} onChange={(event) => setSort(event.currentTarget.value as SortKey)}>
              <option value="global-rank">Global rank</option>
              <option value="global-score">Global score</option>
              <option value="adjusted-score">Adjusted score</option>
              <option value="name">School name</option>
            </select>
          </label>
        </div>

        <div className="quick-actions">
          <button className="action-button" type="button" onClick={resetFilters}>
            <RotateCcw size={16} aria-hidden="true" />
            Reset filters
          </button>
          <button className="action-button" type="button" onClick={exportOverrides} disabled={!overrideCount}>
            <Download size={16} aria-hidden="true" />
            Export overrides
          </button>
          <button className="action-button" type="button" onClick={clearAllOverrides} disabled={!overrideCount}>
            Reset all overrides
          </button>
        </div>

        <p className="panel-note">{caveat}</p>
        <p className="panel-note">Global Score stays visible. Adjusted Score appears when a Personal scoring override is applied.</p>
        <p className="panel-note">Overrides are stored in this browser only.</p>
      </aside>

      <section className="school-browser-results" aria-label="School directory results">
        <div className="feed-heading">
          <div>
            <p className="eyebrow">Full school universe</p>
            <h2>School directory</h2>
            <p>
              Showing {shownRows.length} of {visibleRows.length} matching schools from {schools.length} total.
            </p>
            {sort === "adjusted-score" ? <span className="status-chip neutral">Adjusted sort</span> : null}
          </div>
          <div className="count-block" aria-label="School browser results">
            <strong>{visibleRows.length}</strong>
            <span>matching schools</span>
          </div>
        </div>

        {local.notice ? <p className="state-notice">{local.notice}</p> : null}

        {shownRows.length ? (
          <div className="school-browser-grid">
            {shownRows.map((row) => (
              <BrowserSchoolCard
                key={row.slug}
                row={row}
                schools={schools}
                caveat={caveat}
                local={local}
                isEditing={editingSlug === row.slug}
                onToggleEditor={() => setEditingSlug((current) => (current === row.slug ? "" : row.slug))}
              />
            ))}
          </div>
        ) : (
          <div className="empty-state">
            <h2>No schools match those filters</h2>
            <p>Reset search, state, degree, status, or override filters to restore the directory.</p>
            <button className="action-button" type="button" onClick={resetFilters}>
              Reset filters
            </button>
          </div>
        )}

        {remainingCount > 0 ? (
          <div className="feed-actions" aria-label="More schools">
            <button className="action-button" type="button" onClick={() => setVisibleLimit((current) => current + INITIAL_VISIBLE_COUNT)}>
              Load {Math.min(INITIAL_VISIBLE_COUNT, remainingCount)} more
            </button>
            <button className="action-button" type="button" onClick={() => setVisibleLimit(visibleRows.length)}>
              Show all {visibleRows.length}
            </button>
            <span>{remainingCount} not shown yet</span>
          </div>
        ) : null}
      </section>
    </div>
  );
}

function BrowserSchoolCard({
  row,
  schools,
  caveat,
  local,
  isEditing,
  onToggleEditor,
}: {
  row: SchoolAdjustedScore;
  schools: ProductSchool[];
  caveat: string;
  local: LocalSchoolState;
  isEditing: boolean;
  onToggleEditor: () => void;
}) {
  const school = row.globalScore.school;
  const interested = local.isInterested(school.slug);
  const applying = local.isApplying(school.slug);
  const notInterested = local.isNotInterested(school.slug);
  const compared = local.isCompared(school.slug);
  const override = local.getSchoolWeightOverride(school.slug);

  return (
    <article className="school-card browser-card">
      <div className="school-card-topline">
        <div>
          <p className="eyebrow">
            {school.degree || "Degree not listed"} / {school.city || "City not listed"}, {school.stateAbbrev || school.state || "State not listed"}
          </p>
          <h2>{school.name}</h2>
        </div>
        <div className="rank-stack" aria-label="School browser ranks">
          <div className="rank-pill primary-rank">
            <span>Global Rank</span>
            <strong>{formatRank(row.globalScore.yourRank ?? row.globalScore.baselineRank)}</strong>
          </div>
          {row.overrideApplied ? (
            <div className="rank-pill secondary-rank">
              <span>Adjusted Rank</span>
              <strong>{formatRank(row.adjustedRank)}</strong>
            </div>
          ) : null}
        </div>
      </div>

      <div className="card-meta-row">
        {statusLabels(school.slug, local).map((label) => (
          <span className="status-chip neutral" key={label}>
            {label}
          </span>
        ))}
        {row.overrideApplied ? <span className="status-chip override">Override applied</span> : null}
      </div>

      <dl className="metric-strip compact-metrics">
        <div>
          <dt>Global Score</dt>
          <dd>{formatLiveScore(row.globalScore.yourScore)}</dd>
        </div>
        {row.overrideApplied ? (
          <div>
            <dt>Adjusted Score</dt>
            <dd>{formatLiveScore(row.adjustedScore?.yourScore ?? null)}</dd>
          </div>
        ) : null}
        <div>
          <dt>School MCAT</dt>
          <dd>{metricValue(school.schoolMcat || school.publishedMcatBand)}</dd>
        </div>
        <div>
          <dt>School GPA</dt>
          <dd>{metricValue(school.schoolGpa || school.publishedGpaBand)}</dd>
        </div>
        <div>
          <dt>In-state COA</dt>
          <dd>{formatCurrency(school.costInState)}</dd>
        </div>
        <div>
          <dt>Out-state COA</dt>
          <dd>{formatCurrency(school.costOutState)}</dd>
        </div>
      </dl>

      {row.overrideApplied ? <p className="microcopy">Override applied. Adjusted Score uses school-specific weights, so compare it alongside Global Score.</p> : <p className="microcopy">{caveat}</p>}

      <div className="card-actions" aria-label={`Actions for ${school.name}`}>
        <button
          className={interested ? "action-button selected" : "action-button"}
          type="button"
          aria-pressed={interested}
          onClick={() => (interested ? local.removeInterested(school.slug) : local.addInterested(school.slug))}
        >
          <Star size={16} aria-hidden="true" />
          Interested
        </button>
        <button
          className={applying ? "action-button selected strong" : "action-button strong"}
          type="button"
          aria-pressed={applying}
          onClick={() => (applying ? local.removeApplying(school.slug) : local.addApplying(school.slug))}
        >
          <ClipboardCheck size={16} aria-hidden="true" />
          Applying
        </button>
        <button className={compared ? "action-button selected" : "action-button"} type="button" aria-pressed={compared} onClick={() => local.toggleCompare(school.slug)}>
          <Scale size={16} aria-hidden="true" />
          Compare
        </button>
        <button
          className={notInterested ? "action-button selected danger" : "action-button"}
          type="button"
          aria-pressed={notInterested}
          onClick={() => (notInterested ? local.removeNotInterested(school.slug) : local.addNotInterested(school.slug))}
        >
          <MinusCircle size={16} aria-hidden="true" />
          Not Interested
        </button>
        <button className={isEditing ? "action-button selected" : "action-button"} type="button" aria-expanded={isEditing} onClick={onToggleEditor}>
          <SlidersHorizontal size={16} aria-hidden="true" />
          Personal scoring override
        </button>
        <a className="action-link" href={school.profilePath}>
          Profile
          <ArrowUpRight size={15} aria-hidden="true" />
        </a>
      </div>

      {isEditing ? <SchoolOverrideEditor school={school} schools={schools} preferences={local.preferences} local={local} override={override} /> : null}
    </article>
  );
}

function matchesSearch(row: SchoolAdjustedScore, query: string): boolean {
  const normalized = query.trim().toLowerCase();
  if (!normalized) return true;
  const school = row.globalScore.school;
  return [school.name, school.city, school.state, school.stateAbbrev].join(" ").toLowerCase().includes(normalized);
}

function matchesStatus(row: SchoolAdjustedScore, status: StatusFilter, local: LocalSchoolState): boolean {
  if (status === "all") return true;
  const slug = row.slug;
  if (status === "none") return statusLabels(slug, local)[0] === "None";
  if (status === "interested") return local.isInterested(slug);
  if (status === "applying") return local.isApplying(slug);
  if (status === "notInterested") return local.isNotInterested(slug);
  return local.isCompared(slug);
}

function statusLabels(slug: string, local: LocalSchoolState): string[] {
  const labels: string[] = [];
  if (local.isInterested(slug)) labels.push("Interested");
  if (local.isApplying(slug)) labels.push("Applying");
  if (local.isNotInterested(slug)) labels.push("Not Interested");
  if (local.isCompared(slug)) labels.push("Compared");
  return labels.length ? labels : ["None"];
}

function compareBrowserRows(a: SchoolAdjustedScore, b: SchoolAdjustedScore, sort: SortKey): number {
  if (sort === "name") return a.globalScore.school.name.localeCompare(b.globalScore.school.name);
  if (sort === "global-score") return compareScoreValues(a.globalScore.yourScore, b.globalScore.yourScore) || compareGlobalRank(a, b);
  if (sort === "adjusted-score") return compareScoreValues(adjustedSortValue(a), adjustedSortValue(b)) || compareGlobalRank(a, b);
  return compareGlobalRank(a, b);
}

function compareGlobalRank(a: SchoolAdjustedScore, b: SchoolAdjustedScore): number {
  const aRank = a.globalScore.yourRank ?? a.globalScore.baselineRank ?? 9999;
  const bRank = b.globalScore.yourRank ?? b.globalScore.baselineRank ?? 9999;
  if (aRank !== bRank) return aRank - bRank;
  return a.globalScore.school.name.localeCompare(b.globalScore.school.name);
}

function compareScoreValues(a: number | null, b: number | null): number {
  if (a !== null && b === null) return -1;
  if (a === null && b !== null) return 1;
  if (a !== null && b !== null && a !== b) return b - a;
  return 0;
}

function adjustedSortValue(row: SchoolAdjustedScore): number | null {
  return row.adjustedScore?.yourScore ?? row.globalScore.yourScore;
}

function csvCell(value: string): string {
  return `"${value.replace(/"/g, '""')}"`;
}
