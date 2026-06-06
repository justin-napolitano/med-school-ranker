import { X } from "lucide-react";
import type { ProductSchool } from "../lib/school-utils";
import { buildWhyBullets, formatCurrency, getScoreScreenFit, metricValue } from "../lib/school-utils";
import { useLocalSchoolState } from "./useLocalSchoolState";

type Props = {
  schools: ProductSchool[];
  caveat: string;
};

export function CompareApp({ schools, caveat }: Props) {
  const local = useLocalSchoolState();
  const selectedSchools = local.compare
    .map((slug) => schools.find((school) => school.slug === slug))
    .filter((school): school is ProductSchool => Boolean(school));
  const availableSchools = schools.filter((school) => !local.compare.includes(school.slug)).slice(0, 120);

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
                <span className={`fit-chip ${fit.category}`}>{fit.label}</span>
                <dl className="comparison-metrics">
                  <div>
                    <dt>Rank</dt>
                    <dd>{school.decisionRank ? `#${school.decisionRank}` : school.rankLabel}</dd>
                  </div>
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
