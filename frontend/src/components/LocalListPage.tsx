import { Download } from "lucide-react";
import { scoreSchools } from "../lib/live-scoring";
import type { ProductSchool } from "../lib/school-utils";
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

  return (
    <section className="local-list-surface">
      <div className="feed-heading">
        <div>
          <p className="eyebrow">Local list</p>
          <h2>{title}</h2>
          <p>{cap ? `${selectedSchools.length} of ${cap} schools selected.` : `${selectedSchools.length} schools removed from Build My List.`}</p>
        </div>
        <button className="action-button" type="button" onClick={() => local.exportState(listType)} disabled={!selectedSchools.length}>
          <Download size={16} aria-hidden="true" />
          Export
        </button>
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
          <a className="action-link" href="/">
            Open Build My List
          </a>
        </div>
      )}
    </section>
  );
}
