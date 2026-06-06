import { useEffect, useMemo, useState } from "react";
import { scoreSchools } from "../lib/live-scoring";
import type { ProductSchool } from "../lib/school-utils";
import { filterSchools } from "../lib/school-utils";
import { PreferenceControls } from "./PreferenceControls";
import { SchoolCard } from "./SchoolCard";
import { useLocalSchoolState, type LocalSchoolState } from "./useLocalSchoolState";

type Props = {
  schools: ProductSchool[];
  caveat: string;
  title?: string;
  intro?: string;
  limit?: number;
  showControls?: boolean;
  local?: LocalSchoolState;
};

export function RecommendationFeed(props: Props) {
  if (props.local) return <RecommendationFeedContent {...props} local={props.local} />;
  return <StandaloneRecommendationFeed {...props} />;
}

function StandaloneRecommendationFeed(props: Props) {
  const local = useLocalSchoolState();
  return <RecommendationFeedContent {...props} local={local} />;
}

function RecommendationFeedContent({ schools, caveat, title = "Recommendation Feed", intro, limit = 50, showControls = true, local }: Props & { local: LocalSchoolState }) {
  const [visibleLimit, setVisibleLimit] = useState(limit);
  const filteredSchools = useMemo(
    () => filterSchools(schools, local.preferences).filter((school) => !local.notInterested.includes(school.slug)),
    [schools, local.preferences, local.notInterested],
  );
  const scoredSchools = useMemo(() => scoreSchools(filteredSchools, local.preferences), [filteredSchools, local.preferences]);
  const visibleScores = scoredSchools.slice(0, visibleLimit);
  const remainingCount = Math.max(scoredSchools.length - visibleScores.length, 0);

  useEffect(() => {
    setVisibleLimit(limit);
  }, [
    limit,
    local.preferences.cost,
    local.preferences.degree,
    local.preferences.fit,
    local.preferences.gpa,
    local.preferences.homeState,
    local.preferences.liveWeights,
    local.preferences.mcat,
    local.preferences.ownershipType,
    local.preferences.query,
    local.preferences.region,
    local.preferences.excludedCities,
    local.preferences.excludedStates,
  ]);

  function clearRestoringFilters() {
    local.updatePreference("excludedStates", []);
    local.updatePreference("excludedCities", []);
    local.updatePreference("ownershipType", "all");
    local.updatePreference("query", "");
    local.updatePreference("degree", "all");
    local.updatePreference("region", "all");
    local.updatePreference("cost", "any");
    local.updatePreference("fit", "all");
  }

  return (
    <div className="recommendation-surface">
      {showControls ? (
        <aside className="builder-panel" aria-label="Build inputs">
          <div className="panel-heading">
            <p className="eyebrow">Build My List</p>
            <h2>Applicant inputs</h2>
          </div>
          <PreferenceControls schools={schools} preferences={local.preferences} onChange={local.updatePreference} />
          <p className="panel-note">{caveat}</p>
        </aside>
      ) : null}

      <section className="feed-column" aria-label={title}>
        <div className="feed-heading">
          <div>
            <p className="eyebrow">Live list</p>
            <h2>{title}</h2>
            {intro ? <p>{intro}</p> : null}
          </div>
          <div className="count-block" aria-label="Visible schools">
            <strong>{visibleScores.length}</strong>
            <span>shown / {scoredSchools.length} eligible / {schools.length} total</span>
          </div>
        </div>

        {local.notice ? <p className="state-notice">{local.notice}</p> : null}

        {visibleScores.length ? (
          <div className="card-feed">
            {visibleScores.map((score) => (
              <SchoolCard key={score.school.slug} school={score.school} liveScore={score} preferences={local.preferences} caveat={caveat} actions={local} />
            ))}
          </div>
        ) : (
          <div className="empty-state">
            <h2>No eligible schools</h2>
            <p>Clear exclusions, ownership, search, or score-screen filters to restore schools to Build My List.</p>
            <button className="action-button" type="button" onClick={clearRestoringFilters}>
              Clear filters
            </button>
          </div>
        )}

        {remainingCount > 0 ? (
          <div className="feed-actions" aria-label="More schools">
            <button className="action-button" type="button" onClick={() => setVisibleLimit((current) => current + 50)}>
              Load 50 more
            </button>
            <button className="action-button" type="button" onClick={() => setVisibleLimit(scoredSchools.length)}>
              Show all {scoredSchools.length}
            </button>
            <span>{remainingCount} not shown yet</span>
          </div>
        ) : null}
      </section>
    </div>
  );
}
