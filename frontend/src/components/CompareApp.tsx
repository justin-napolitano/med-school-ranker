import { X } from "lucide-react";
import { useMemo } from "react";
import { formatLiveScore, formatRank, scoreSchoolsWithOverrides } from "../lib/live-scoring";
import type { ProductSchool } from "../lib/school-utils";
import { buildWhyBullets, formatCurrency, getScoreScreenFit, metricValue } from "../lib/school-utils";
import { useLocalSchoolState, type LocalSchoolState } from "./useLocalSchoolState";

type Props = {
  schools: ProductSchool[];
  caveat: string;
  local?: LocalSchoolState;
};

export function CompareApp(props: Props) {
  if (props.local) return <CompareAppContent {...props} local={props.local} />;
  return <StandaloneCompareApp {...props} />;
}

function StandaloneCompareApp(props: Props) {
  const local = useLocalSchoolState();
  return <CompareAppContent {...props} local={local} />;
}

function CompareAppContent({ schools, caveat, local }: Props & { local: LocalSchoolState }) {
  const schoolBySlug = useMemo(() => new Map(schools.map((school) => [school.slug, school])), [schools]);
  const selectedSchools = useMemo(
    () => local.compare.map((slug) => schoolBySlug.get(slug)).filter((school): school is ProductSchool => Boolean(school)),
    [local.compare, schoolBySlug],
  );
  const availableSchools = useMemo(() => schools.filter((school) => !local.compare.includes(school.slug)).slice(0, 120), [schools, local.compare]);
  const scoreRowsBySlug = useMemo(
    () => new Map(scoreSchoolsWithOverrides(schools, local.preferences, local.schoolWeightOverrides).map((row) => [row.slug, row])),
    [schools, local.preferences, local.schoolWeightOverrides],
  );

  return (
    <section className="compare-surface">
      <div className="feed-heading">
        <div>
          <p className="eyebrow">Side by side</p>
          <h2>Compare</h2>
          <p>{caveat}</p>
        </div>
        <label className="inline-picker">
          <span>Add school</span>
          <select value="" onChange={(event) => event.currentTarget.value && local.toggleCompare(event.currentTarget.value)}>
            <option value="">Choose</option>
            {availableSchools.map((school) => (
              <option key={school.slug} value={school.slug}>
                {school.name}
              </option>
            ))}
          </select>
        </label>
      </div>

      {local.notice ? <p className="state-notice">{local.notice}</p> : null}

      {selectedSchools.length ? (
        <div className="compare-grid">
          {selectedSchools.map((school) => {
            const fit = getScoreScreenFit(school, local.preferences);
            const scoreRow = scoreRowsBySlug.get(school.slug);
            return (
              <article className="compare-card" key={school.slug}>
                <div className="compare-card-header">
                  <div>
                    <p className="eyebrow">
                      {school.degree} / {school.city}, {school.stateAbbrev}
                    </p>
                    <h2>{school.name}</h2>
                  </div>
                  <button className="icon-button" type="button" onClick={() => local.toggleCompare(school.slug)} aria-label={`Remove ${school.name} from compare`}>
                    <X size={18} aria-hidden="true" />
                  </button>
                </div>
                {scoreRow?.overrideApplied ? <span className="status-chip override">Override applied</span> : null}
                <span className={`fit-chip ${fit.category}`}>{fit.label}</span>
                <dl className="comparison-metrics">
                  <div>
                    <dt>Global Rank</dt>
                    <dd>{formatRank(scoreRow?.globalScore.yourRank ?? school.decisionRank ?? school.overallRank)}</dd>
                  </div>
                  <div>
                    <dt>Global Score</dt>
                    <dd>{formatLiveScore(scoreRow?.globalScore.yourScore ?? null)}</dd>
                  </div>
                  {scoreRow?.overrideApplied ? (
                    <>
                      <div>
                        <dt>Adjusted Rank</dt>
                        <dd>{formatRank(scoreRow.adjustedRank)}</dd>
                      </div>
                      <div>
                        <dt>Adjusted Score</dt>
                        <dd>{formatLiveScore(scoreRow.adjustedScore?.yourScore ?? null)}</dd>
                      </div>
                    </>
                  ) : null}
                  <div>
                    <dt>MCAT</dt>
                    <dd>{metricValue(school.schoolMcat || school.publishedMcatBand)}</dd>
                  </div>
                  <div>
                    <dt>GPA</dt>
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
                  <div>
                    <dt>Source quality</dt>
                    <dd>{school.statsQuality || "Not available"}</dd>
                  </div>
                </dl>
                <ul className="compact-bullets">
                  {buildWhyBullets(school)
                    .slice(0, 3)
                    .map((bullet) => (
                      <li key={bullet}>{bullet}</li>
                    ))}
                </ul>
                <a className="action-link" href={school.profilePath}>
                  Open profile
                </a>
              </article>
            );
          })}
        </div>
      ) : (
        <div className="empty-state">
          <h2>No schools selected for compare</h2>
          <p>Add schools from recommendation cards or the picker above.</p>
        </div>
      )}
    </section>
  );
}
