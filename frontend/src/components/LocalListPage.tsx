import { Download } from "lucide-react";
import { scoreSchools } from "../lib/live-scoring";
import type { ProductSchool } from "../lib/school-utils";
import { withBase } from "../lib/site-url";
import { PreferenceControls } from "./PreferenceControls";
import { SchoolCard } from "./SchoolCard";
import { useLocalSchoolState } from "./useLocalSchoolState";

type Props = {
  schools: ProductSchool[];
  caveat: string;
  listType: "interested" | "applying" | "notInterested";
};

export function LocalListPage({ schools, caveat, listType }: Props) {
  const local = useLocalSchoolState();
  const slugs = listType === "interested" ? local.interested : listType === "applying" ? local.applying : local.notInterested;
  const selectedSchools = slugs
    .map((slug) => schools.find((school) => school.slug === slug))
    .filter((school): school is ProductSchool => Boolean(school));
  const scoredSchools = scoreSchools(selectedSchools, local.preferences);
  const title = listType === "interested" ? "Interested" : listType === "applying" ? "Applying" : "Not Interested";
  const cap = listType === "interested" ? 50 : listType === "applying" ? 25 : null;
  const showRankingControls = listType === "interested" || listType === "applying";
  const rankedCount = scoredSchools.filter((score) => score.yourScore !== null).length;
  const intro = showRankingControls
    ? "Reweight this selected list with the same browser-local inputs used on Build My List. Cards re-sort by Your Rank; Baseline Rank stays visible."
    : "Schools on this list are removed from Build My List until restored.";

  return (
    <div className={showRankingControls ? "recommendation-surface" : "local-list-surface"}>
      {showRankingControls ? (
        <aside className="builder-panel" aria-label={`${title} ranking inputs`}>
          <div className="panel-heading">
            <p className="eyebrow">Selected-list ranking</p>
            <h2>Reweight {title}</h2>
          </div>
          <PreferenceControls schools={selectedSchools.length ? selectedSchools : schools} preferences={local.preferences} onChange={local.updatePreference} mode="scoring" />
          <p className="panel-note">{caveat}</p>
        </aside>
      ) : null}

      <section className="feed-column" aria-label={title}>
        <div className="feed-heading">
          <div>
            <p className="eyebrow">Local list</p>
            <h2>{title}</h2>
            <p>{cap ? `${selectedSchools.length} of ${cap} schools selected. ${intro}` : `${selectedSchools.length} schools removed from Build My List. ${intro}`}</p>
          </div>
          <div className="list-heading-actions">
            {showRankingControls ? (
              <div className="count-block" aria-label="Ranked selected schools">
                <strong>{rankedCount}</strong>
                <span>ranked / {selectedSchools.length} selected</span>
              </div>
            ) : null}
            <button className="action-button" type="button" onClick={() => local.exportState(listType)} disabled={!selectedSchools.length}>
              <Download size={16} aria-hidden="true" />
              Export
            </button>
          </div>
        </div>

        {local.notice ? <p className="state-notice">{local.notice}</p> : null}

        {selectedSchools.length ? (
          <div className="card-feed">
            {scoredSchools.map((score) => (
              <SchoolCard key={score.school.slug} school={score.school} liveScore={score} preferences={local.preferences} caveat={caveat} actions={local} />
            ))}
          </div>
        ) : (
          <div className="empty-state">
            <h2>No schools selected yet</h2>
            <p>Use Build My List to add schools to this local list.</p>
            <a className="action-link" href={withBase("/")}>
              Open Build My List
            </a>
          </div>
        )}
      </section>
    </div>
  );
}
