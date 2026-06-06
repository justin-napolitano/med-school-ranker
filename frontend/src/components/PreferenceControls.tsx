import type { PreferenceState, ProductSchool } from "../lib/school-utils";
import { statesForSchools } from "../lib/school-utils";

type Props = {
  preferences: PreferenceState;
  schools: ProductSchool[];
  onChange: <K extends keyof PreferenceState>(key: K, value: PreferenceState[K]) => void;
  compact?: boolean;
};

export function PreferenceControls({ preferences, schools, onChange, compact = false }: Props) {
  const states = statesForSchools(schools);

  return (
    <form className={compact ? "control-grid compact" : "control-grid"} aria-label="Applicant list inputs">
      <label>
        <span>MCAT</span>
        <input
          inputMode="numeric"
          value={preferences.mcat}
          onChange={(event) => onChange("mcat", event.currentTarget.value)}
          placeholder="512"
          aria-label="Applicant MCAT"
        />
      </label>
      <label>
        <span>GPA</span>
        <input
          inputMode="decimal"
          value={preferences.gpa}
          onChange={(event) => onChange("gpa", event.currentTarget.value)}
          placeholder="3.70"
          aria-label="Applicant GPA"
        />
      </label>
      <label>
        <span>Home state</span>
        <select value={preferences.homeState} onChange={(event) => onChange("homeState", event.currentTarget.value)}>
          <option value="">Any</option>
          {states.map((state) => (
            <option value={state} key={state}>
              {state}
            </option>
          ))}
        </select>
      </label>
      <label>
        <span>Degree</span>
        <select value={preferences.degree} onChange={(event) => onChange("degree", event.currentTarget.value as PreferenceState["degree"])}>
          <option value="all">MD and DO</option>
          <option value="MD">MD</option>
          <option value="DO">DO</option>
        </select>
      </label>
      <label>
        <span>Region</span>
        <select value={preferences.region} onChange={(event) => onChange("region", event.currentTarget.value)}>
          <option value="all">All regions</option>
          <option value="Northeast">Northeast</option>
          <option value="South">South</option>
          <option value="Midwest">Midwest</option>
          <option value="West">West</option>
        </select>
      </label>
      <label>
        <span>Cost data</span>
        <select value={preferences.cost} onChange={(event) => onChange("cost", event.currentTarget.value as PreferenceState["cost"])}>
          <option value="any">Any</option>
          <option value="has-cost">Has cost data</option>
          <option value="lower-cost">Lower listed cost first</option>
        </select>
      </label>
      <label>
        <span>Data quality</span>
        <select
          value={preferences.dataConfidence}
          onChange={(event) => onChange("dataConfidence", event.currentTarget.value as PreferenceState["dataConfidence"])}
        >
          <option value="any">Any</option>
          <option value="medium-plus">Medium or high MCAT/GPA source quality</option>
        </select>
      </label>
      <label>
        <span>Score-screen fit</span>
        <select value={preferences.fit} onChange={(event) => onChange("fit", event.currentTarget.value as PreferenceState["fit"])}>
          <option value="all">All</option>
          <option value="within">Within published range</option>
          <option value="near">Near published range</option>
          <option value="below">Below published range</option>
          <option value="above">Above published range</option>
          <option value="needs-inputs">Needs inputs or data</option>
        </select>
      </label>
      <label className="wide">
        <span>Search</span>
        <input
          value={preferences.query}
          onChange={(event) => onChange("query", event.currentTarget.value)}
          placeholder="School, city, state"
          aria-label="Search schools"
        />
      </label>
    </form>
  );
}
