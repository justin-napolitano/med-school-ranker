import { ArrowUpRight, ClipboardCheck, Scale, Star } from "lucide-react";
import type { PreferenceState, ProductSchool } from "../lib/school-utils";
import { buildWhyBullets, formatCurrency, getScoreScreenFit, metricValue } from "../lib/school-utils";

type LocalActions = {
  addInterested: (slug: string) => void;
  removeInterested: (slug: string) => void;
  addApplying: (slug: string) => void;
  removeApplying: (slug: string) => void;
  toggleCompare: (slug: string) => void;
  isInterested: (slug: string) => boolean;
  isApplying: (slug: string) => boolean;
  isCompared: (slug: string) => boolean;
};

type Props = {
  school: ProductSchool;
  preferences: PreferenceState;
  caveat: string;
  actions: LocalActions;
  compact?: boolean;
};

export function SchoolCard({ school, preferences, caveat, actions, compact = false }: Props) {
  const fit = getScoreScreenFit(school, preferences);
  const whyBullets = buildWhyBullets(school);
  const interested = actions.isInterested(school.slug);
  const applying = actions.isApplying(school.slug);
  const compared = actions.isCompared(school.slug);

  return (
    <article className={compact ? "school-card compact" : "school-card"}>
      <div className="school-card-topline">
        <div>
          <p className="eyebrow">
            {school.degree || "Degree not listed"} / {school.city || "City not listed"}, {school.stateAbbrev || school.state || "State not listed"}
          </p>
          <h2>{school.name}</h2>
        </div>
        <div className="rank-pill" aria-label="Decision rank">
          <span>{school.rankLabel}</span>
          <strong>{school.decisionRank ? `#${school.decisionRank}` : "Unranked"}</strong>
        </div>
      </div>

      <div className="fit-line">
        <span className={`fit-chip ${fit.category}`}>{fit.label}</span>
        <span className="microcopy">{caveat}</span>
      </div>

      <dl className="metric-strip">
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

      <div className="why-block">
        <h3>Why it ranks here</h3>
        <ul>
          {whyBullets.map((bullet) => (
            <li key={bullet}>{bullet}</li>
          ))}
        </ul>
      </div>

      <div className="card-meta-row">
        <span className={`status-chip ${school.rankConfidence || "provisional"}`}>{school.rankConfidence || "provisional"}</span>
        <span className="status-chip neutral">Stats: {school.statsQuality || "not available"}</span>
        <span className="status-chip neutral">{school.rankBand || "Incomplete data"}</span>
      </div>

      <div className="card-actions" aria-label={`Actions for ${school.name}`}>
        <button
          className={interested ? "action-button selected" : "action-button"}
          type="button"
          aria-pressed={interested}
          onClick={() => (interested ? actions.removeInterested(school.slug) : actions.addInterested(school.slug))}
        >
          <Star size={16} aria-hidden="true" />
          Interested
        </button>
        <button
          className={applying ? "action-button selected strong" : "action-button strong"}
          type="button"
          aria-pressed={applying}
          onClick={() => (applying ? actions.removeApplying(school.slug) : actions.addApplying(school.slug))}
        >
          <ClipboardCheck size={16} aria-hidden="true" />
          Applying
        </button>
        <button
          className={compared ? "action-button selected" : "action-button"}
          type="button"
          aria-pressed={compared}
          onClick={() => actions.toggleCompare(school.slug)}
        >
          <Scale size={16} aria-hidden="true" />
          Compare
        </button>
        <a className="action-link" href={school.profilePath}>
          Profile
          <ArrowUpRight size={15} aria-hidden="true" />
        </a>
      </div>
    </article>
  );
}
