import { ArrowUpRight, ClipboardCheck, MinusCircle, Scale, Star } from "lucide-react";
import type { LiveSchoolScore, SchoolAdjustedScore } from "../lib/live-scoring";
import { buildLiveFactorBullets, formatLiveScore, formatRank } from "../lib/live-scoring";
import type { PreferenceState, ProductSchool } from "../lib/school-utils";
import { buildWhyBullets, formatCurrency, getScoreScreenFit, metricValue } from "../lib/school-utils";

type LocalActions = {
  addInterested: (slug: string) => void;
  removeInterested: (slug: string) => void;
  addApplying: (slug: string) => void;
  removeApplying: (slug: string) => void;
  addNotInterested: (slug: string) => void;
  removeNotInterested: (slug: string) => void;
  toggleCompare: (slug: string) => void;
  isInterested: (slug: string) => boolean;
  isApplying: (slug: string) => boolean;
  isNotInterested: (slug: string) => boolean;
  isCompared: (slug: string) => boolean;
};

type Props = {
  school: ProductSchool;
  liveScore?: LiveSchoolScore;
  preferences: PreferenceState;
  caveat: string;
  actions: LocalActions;
  scoreAdjustment?: SchoolAdjustedScore;
  compact?: boolean;
};

export function SchoolCard({ school, liveScore, preferences, caveat, actions, scoreAdjustment, compact = false }: Props) {
  const fit = getScoreScreenFit(school, preferences);
  const whyBullets = buildWhyBullets(school);
  const liveBullets = liveScore ? buildLiveFactorBullets(liveScore) : [];
  const interested = actions.isInterested(school.slug);
  const applying = actions.isApplying(school.slug);
  const notInterested = actions.isNotInterested(school.slug);
  const compared = actions.isCompared(school.slug);
  const overrideApplied = Boolean(scoreAdjustment?.overrideApplied);
  const globalScore = scoreAdjustment?.globalScore || liveScore || null;
  const adjustedScore = scoreAdjustment?.adjustedScore || null;

  return (
    <article className={compact ? "school-card compact" : "school-card"}>
      <div className="school-card-topline">
        <div>
          <p className="eyebrow">
            {school.degree || "Degree not listed"} / {school.city || "City not listed"}, {school.stateAbbrev || school.state || "State not listed"}
          </p>
          <h2>{school.name}</h2>
        </div>
        <div className="rank-stack" aria-label="Live and baseline rank">
          <div className="rank-pill primary-rank">
            <span>Your Rank</span>
            <strong>{formatRank(liveScore?.yourRank ?? null)}</strong>
          </div>
          <div className="rank-pill secondary-rank">
            <span>Baseline Rank</span>
            <strong>{formatRank(liveScore?.baselineRank ?? school.decisionRank ?? school.overallRank)}</strong>
          </div>
        </div>
      </div>

      <div className="fit-line">
        <span className={`fit-chip ${fit.category}`}>{fit.label}</span>
        <span className="microcopy">{caveat}</span>
      </div>

      <dl className="metric-strip">
        {overrideApplied ? (
          <>
            <div>
              <dt>Global Score</dt>
              <dd>{formatLiveScore(globalScore?.yourScore ?? null)}</dd>
            </div>
            <div>
              <dt>Adjusted Score</dt>
              <dd>{formatLiveScore(adjustedScore?.yourScore ?? null)}</dd>
            </div>
          </>
        ) : (
          <div>
            <dt>Your Score</dt>
            <dd>{formatLiveScore(liveScore?.yourScore ?? null)}</dd>
          </div>
        )}
        <div>
          <dt>Coverage</dt>
          <dd>{liveScore ? `${liveScore.liveCoverage.label} (${liveScore.liveCoverage.available}/${liveScore.liveCoverage.possible})` : "Needs data"}</dd>
        </div>
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
        <h3>Live fit factors</h3>
        {liveBullets.length ? (
          <ul>
            {liveBullets.map((bullet) => (
              <li key={bullet}>{bullet}</li>
            ))}
          </ul>
        ) : (
          <p className="microcopy">Live scoring is available in Build My List when card context is scored.</p>
        )}
      </div>

      <div className="why-block">
        <h3>Generated baseline context</h3>
        <ul>
          {whyBullets.map((bullet) => (
            <li key={bullet}>{bullet}</li>
          ))}
        </ul>
      </div>

      <div className="card-meta-row">
        {overrideApplied ? <span className="status-chip override">Override applied</span> : null}
        <span className={`status-chip ${liveScore?.liveCoverage.label || "neutral"}`}>Live coverage: {liveScore?.liveCoverage.label || "not scored"}</span>
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
        <button
          className={notInterested ? "action-button selected danger" : "action-button"}
          type="button"
          aria-pressed={notInterested}
          onClick={() => (notInterested ? actions.removeNotInterested(school.slug) : actions.addNotInterested(school.slug))}
        >
          <MinusCircle size={16} aria-hidden="true" />
          Not Interested
        </button>
        <a className="action-link" href={school.profilePath}>
          Profile
          <ArrowUpRight size={15} aria-hidden="true" />
        </a>
      </div>
    </article>
  );
}
