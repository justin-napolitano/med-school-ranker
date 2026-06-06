import { Download } from "lucide-react";
import type { ProductSchool } from "../lib/school-utils";
import { SchoolCard } from "./SchoolCard";
import { useLocalSchoolState } from "./useLocalSchoolState";

type Props = {
  schools: ProductSchool[];
  caveat: string;
  listType: "interested" | "applying";
};

export function LocalListPage({ schools, caveat, listType }: Props) {
  const local = useLocalSchoolState();
  const slugs = listType === "interested" ? local.interested : local.applying;
  const selectedSchools = slugs
    .map((slug) => schools.find((school) => school.slug === slug))
    .filter((school): school is ProductSchool => Boolean(school));
  const title = listType === "interested" ? "Interested" : "Applying";
  const cap = listType === "interested" ? 50 : 25;

  return (
    <section className="local-list-surface">
      <div className="feed-heading">
        <div>
          <p className="eyebrow">Local list</p>
          <h2>{title}</h2>
          <p>
            {selectedSchools.length} of {cap} schools selected.
          </p>
        </div>
        <button className="action-button" type="button" onClick={() => local.exportState(listType)} disabled={!selectedSchools.length}>
          <Download size={16} aria-hidden="true" />
          Export
        </button>
      </div>

      {local.notice ? <p className="state-notice">{local.notice}</p> : null}

      {selectedSchools.length ? (
        <div className="card-feed">
          {selectedSchools.map((school) => (
            <SchoolCard key={school.slug} school={school} preferences={local.preferences} caveat={caveat} actions={local} />
          ))}
        </div>
      ) : (
        <div className="empty-state">
          <h2>No schools selected yet</h2>
          <p>Use the recommendation cards to add schools to this local list.</p>
          <a className="action-link" href="/recommendations/">
            Open recommendations
          </a>
        </div>
      )}
    </section>
  );
}
