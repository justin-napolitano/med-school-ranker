import { useMemo } from "react";
import type { ProductSchool } from "../lib/school-utils";
import { filterSchools } from "../lib/school-utils";
import { PreferenceControls } from "./PreferenceControls";
import { SchoolCard } from "./SchoolCard";
import { useLocalSchoolState } from "./useLocalSchoolState";

type Props = {
  schools: ProductSchool[];
  caveat: string;
  title?: string;
  intro?: string;
  limit?: number;
  showControls?: boolean;
};

export function RecommendationFeed({ schools, caveat, title = "Recommendation Feed", intro, limit = 24, showControls = true }: Props) {
  const local = useLocalSchoolState();
  const visibleSchools = useMemo(
    () => filterSchools(schools, local.preferences).slice(0, limit),
    [schools, local.preferences, limit],
  );

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
            <strong>{visibleSchools.length}</strong>
            <span>shown</span>
          </div>
        </div>

        {local.notice ? <p className="state-notice">{local.notice}</p> : null}

        <div className="card-feed">
          {visibleSchools.map((school) => (
            <SchoolCard key={school.slug} school={school} preferences={local.preferences} caveat={caveat} actions={local} />
          ))}
        </div>
      </section>
    </div>
  );
}
