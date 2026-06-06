import { ClipboardCheck, MinusCircle, RotateCcw, Scale, SlidersHorizontal, Star } from "lucide-react";
import { useMemo, useState } from "react";
import { appHref } from "../lib/app-routing";
import { buildLiveFactorBullets, formatLiveScore, formatRank, scoreSchoolsWithOverrides } from "../lib/live-scoring";
import type { ProductSchool } from "../lib/school-utils";
import { buildWhyBullets, formatCurrency, getScoreScreenFit, metricValue } from "../lib/school-utils";
import { SchoolOverrideEditor } from "./SchoolOverrideEditor";
import type { LocalSchoolState } from "./useLocalSchoolState";

type Props = {
  schools: ProductSchool[];
  slug: string;
  caveat: string;
  local: LocalSchoolState;
};

export function AppSchoolProfileView({ schools, slug, caveat, local }: Props) {
  const [showOverrideEditor, setShowOverrideEditor] = useState(false);
  const school = useMemo(() => schools.find((item) => item.slug === slug) || null, [schools, slug]);
  const scoreRow = useMemo(() => {
    if (!school) return null;
    return scoreSchoolsWithOverrides(schools, local.preferences, local.schoolWeightOverrides).find((score) => score.slug === school.slug) || null;
  }, [schools, school, local.preferences, local.schoolWeightOverrides]);

  if (!school) {
    return (
      <div className="empty-state">
        <h2>School profile not found</h2>
        <p>This static build does not include a profile for that school slug.</p>
        <a className="action-link" href={appHref("/")}>
          Open Build My List
        </a>
      </div>
    );
  }

  const fit = getScoreScreenFit(school, local.preferences);
  const whyBullets = buildWhyBullets(school);
  const liveScore = scoreRow?.globalScore || null;
  const liveBullets = liveScore ? buildLiveFactorBullets(liveScore) : [];
  const adjustedBullets = scoreRow?.adjustedScore ? buildLiveFactorBullets(scoreRow.adjustedScore) : [];
  const interested = local.isInterested(school.slug);
  const applying = local.isApplying(school.slug);
  const notInterested = local.isNotInterested(school.slug);
  const compared = local.isCompared(school.slug);
  const override = local.getSchoolWeightOverride(school.slug);

  return (
    <>
      <section className="profile-action-panel" aria-label={`${school.name} local actions`}>
        <div className="fit-line">
          <span className={`fit-chip ${fit.category}`}>{fit.label}</span>
          {scoreRow?.overrideApplied ? <span className="status-chip override">Override applied</span> : null}
          <span className="microcopy">{caveat}</span>
        </div>
        <dl className="metric-strip">
          <div>
            <dt>Rank label</dt>
            <dd>{school.rankLabel || "Unranked"}</dd>
          </div>
          <div>
            <dt>Global Rank</dt>
            <dd>{formatRank(liveScore?.yourRank ?? null)}</dd>
          </div>
          <div>
            <dt>Baseline Rank</dt>
            <dd>{formatRank(liveScore?.baselineRank ?? school.decisionRank ?? school.overallRank)}</dd>
          </div>
          <div>
            <dt>Global Score</dt>
            <dd>{formatLiveScore(liveScore?.yourScore ?? null)}</dd>
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
            <dt>Coverage</dt>
            <dd>{liveScore ? `${liveScore.liveCoverage.label} (${liveScore.liveCoverage.available}/${liveScore.liveCoverage.possible})` : "Needs data"}</dd>
          </div>
        </dl>
        {scoreRow?.overrideApplied ? <p className="state-notice">Override applied. Adjusted Score uses school-specific weights, so compare it alongside Global Score.</p> : null}
        {local.notice ? <p className="state-notice">{local.notice}</p> : null}
        <div className="card-actions profile-actions" aria-label={`Actions for ${school.name}`}>
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
          <button className={showOverrideEditor ? "action-button selected" : "action-button"} type="button" aria-expanded={showOverrideEditor} onClick={() => setShowOverrideEditor((current) => !current)}>
            <SlidersHorizontal size={16} aria-hidden="true" />
            Edit scoring override
          </button>
          {scoreRow?.overrideApplied ? (
            <button
              className="action-button"
              type="button"
              onClick={() => {
                local.removeSchoolWeightOverride(school.slug);
                setShowOverrideEditor(false);
              }}
            >
              <RotateCcw size={16} aria-hidden="true" />
              Reset to global
            </button>
          ) : null}
        </div>
        {showOverrideEditor ? <SchoolOverrideEditor school={school} schools={schools} preferences={local.preferences} local={local} override={override} /> : null}
      </section>

      <section className="profile-grid">
        <article className="profile-section">
          <h2>Score-screen Context</h2>
          <span className={`fit-chip ${fit.category}`}>{fit.label}</span>
          <dl className="profile-metrics">
            <div>
              <dt>Published MCAT</dt>
              <dd>{metricValue(school.schoolMcat || school.publishedMcatBand)}</dd>
            </div>
            <div>
              <dt>Published GPA</dt>
              <dd>{metricValue(school.schoolGpa || school.publishedGpaBand)}</dd>
            </div>
            <div>
              <dt>MCAT/GPA source quality</dt>
              <dd>{school.statsQuality || "Not available"}</dd>
            </div>
          </dl>
        </article>

        <article className="profile-section">
          <h2>Cost Context</h2>
          <dl className="profile-metrics">
            <div>
              <dt>Estimated in-state COA</dt>
              <dd>{formatCurrency(school.costInState)}</dd>
            </div>
            <div>
              <dt>Estimated out-of-state COA</dt>
              <dd>{formatCurrency(school.costOutState)}</dd>
            </div>
            <div>
              <dt>Cost source confidence</dt>
              <dd>{school.costConfidence || "Not available"}</dd>
            </div>
          </dl>
        </article>

        <article className="profile-section wide">
          <h2>Why It Ranks Here</h2>
          <ul>
            {whyBullets.map((bullet) => (
              <li key={bullet}>{bullet}</li>
            ))}
          </ul>
        </article>

        <article className="profile-section wide">
          <h2>Live fit factors</h2>
          {liveBullets.length ? (
            <ul>
              {liveBullets.map((bullet) => (
                <li key={bullet}>{bullet}</li>
              ))}
            </ul>
          ) : (
            <p>Live scoring appears when applicant inputs and weighted school data are present.</p>
          )}
        </article>

        {scoreRow?.overrideApplied ? (
          <article className="profile-section wide">
            <h2>Adjusted fit factors</h2>
            <p>Adjusted Score uses this school&apos;s Personal scoring override. Global Score remains the shared baseline.</p>
            <ul>
              {adjustedBullets.map((bullet) => (
                <li key={bullet}>{bullet}</li>
              ))}
            </ul>
          </article>
        ) : null}

        <article className="profile-section">
          <h2>Data Status</h2>
          <dl className="profile-metrics">
            <div>
              <dt>Rank confidence</dt>
              <dd>{school.rankConfidence || "provisional"}</dd>
            </div>
            <div>
              <dt>Admissions policies</dt>
              <dd>{school.policyCount}</dd>
            </div>
            <div>
              <dt>Letter rows</dt>
              <dd>{school.letterCount}</dd>
            </div>
            <div>
              <dt>Stats source quality</dt>
              <dd>{school.statsQuality || "Not available"}</dd>
            </div>
          </dl>
        </article>

        <article className="profile-section">
          <h2>Source</h2>
          <p>{school.sourceName || "Source name not available in payload."}</p>
          {school.sourceUrl ? (
            <a className="action-link" href={school.sourceUrl}>
              Open source
            </a>
          ) : null}
        </article>
      </section>
    </>
  );
}
