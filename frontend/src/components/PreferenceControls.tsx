import { RotateCcw, X } from "lucide-react";
import { liveWeightDescriptions, liveWeightPresets } from "../lib/live-scoring";
import type { LiveWeightKey, PreferenceState, ProductSchool } from "../lib/school-utils";
import {
  cityLabelFromKey,
  cityOptionsForSchools,
  defaultLiveWeights,
  ownershipLabel,
  schoolsHaveOwnershipLabels,
  stateLabel,
  statesForSchools,
} from "../lib/school-utils";

type Props = {
  preferences: PreferenceState;
  schools: ProductSchool[];
  onChange: <K extends keyof PreferenceState>(key: K, value: PreferenceState[K]) => void;
  compact?: boolean;
  mode?: "full" | "scoring";
};

const weightOrder: LiveWeightKey[] = ["mcatFit", "gpaFit", "stateFit", "costFit", "baselineAttendance"];

export function PreferenceControls({ preferences, schools, onChange, compact = false, mode = "full" }: Props) {
  const states = statesForSchools(schools);
  const cityOptions = cityOptionsForSchools(schools);
  const hasOwnershipLabels = schoolsHaveOwnershipLabels(schools);
  const availableStates = states.filter((state) => !preferences.excludedStates.includes(state));
  const availableCities = cityOptions.filter((city) => !preferences.excludedCities.includes(city));
  const showFilters = mode === "full";

  function addExcludedState(state: string) {
    if (!state || preferences.excludedStates.includes(state)) return;
    onChange("excludedStates", [...preferences.excludedStates, state].sort());
  }

  function removeExcludedState(state: string) {
    onChange(
      "excludedStates",
      preferences.excludedStates.filter((item) => item !== state),
    );
  }

  function addExcludedCity(city: string) {
    if (!city || preferences.excludedCities.includes(city)) return;
    onChange("excludedCities", [...preferences.excludedCities, city].sort((a, b) => cityLabelFromKey(a).localeCompare(cityLabelFromKey(b))));
  }

  function removeExcludedCity(city: string) {
    onChange(
      "excludedCities",
      preferences.excludedCities.filter((item) => item !== city),
    );
  }

  function updateWeight(key: LiveWeightKey, value: number) {
    onChange("liveWeights", { ...preferences.liveWeights, [key]: value });
  }

  function applyPreset(preset: (typeof liveWeightPresets)[number]) {
    onChange("liveWeights", preset.weights);
    if (preset.homeState) onChange("homeState", preset.homeState);
  }

  function clearExclusions() {
    onChange("excludedStates", []);
    onChange("excludedCities", []);
  }

  function clearFilters() {
    onChange("degree", "all");
    onChange("region", "all");
    onChange("cost", "any");
    onChange("fit", "all");
    onChange("query", "");
    onChange("ownershipType", "all");
    clearExclusions();
  }

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
              {stateLabel(state)}
            </option>
          ))}
        </select>
      </label>
      {showFilters ? (
        <>
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
            <span>Exclude state</span>
            <select value="" onChange={(event) => addExcludedState(event.currentTarget.value)}>
              <option value="">Choose state</option>
              {availableStates.map((state) => (
                <option value={state} key={state}>
                  {stateLabel(state)}
                </option>
              ))}
            </select>
          </label>
          <label>
            <span>Exclude city</span>
            <select value="" onChange={(event) => addExcludedCity(event.currentTarget.value)}>
              <option value="">Choose city</option>
              {availableCities.map((city) => (
                <option value={city} key={city}>
                  {cityLabelFromKey(city)}
                </option>
              ))}
            </select>
          </label>
          <label>
            <span>Institution ownership</span>
            <select
              value={hasOwnershipLabels ? preferences.ownershipType : "unknown"}
              disabled={!hasOwnershipLabels}
              onChange={(event) => onChange("ownershipType", event.currentTarget.value as PreferenceState["ownershipType"])}
            >
              {hasOwnershipLabels ? (
                <>
                  <option value="all">All ownership types</option>
                  <option value="public">Public</option>
                  <option value="private">Private</option>
                  <option value="unknown">Unknown</option>
                </>
              ) : (
                <option value="unknown">Unknown</option>
              )}
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
          <div className="wide filter-tools" aria-label="Active exclusions and filter tools">
            {hasOwnershipLabels ? null : <p className="control-note">Ownership labels are not populated yet, so ownership filtering is disabled instead of inferred.</p>}
            <div className="quick-actions">
              <button className="action-button" type="button" onClick={() => addExcludedState("TX")} disabled={preferences.excludedStates.includes("TX")}>
                Exclude TX
              </button>
              <button className="action-button" type="button" onClick={clearExclusions} disabled={!preferences.excludedStates.length && !preferences.excludedCities.length}>
                Clear exclusions
              </button>
              <button className="action-button" type="button" onClick={clearFilters}>
                Clear filters
              </button>
            </div>
            {preferences.excludedStates.length || preferences.excludedCities.length ? (
              <div className="chip-row" aria-label="Excluded geography">
                {preferences.excludedStates.map((state) => (
                  <button className="filter-chip" type="button" key={state} onClick={() => removeExcludedState(state)}>
                    {state}
                    <X size={13} aria-hidden="true" />
                  </button>
                ))}
                {preferences.excludedCities.map((city) => (
                  <button className="filter-chip" type="button" key={city} onClick={() => removeExcludedCity(city)}>
                    {cityLabelFromKey(city)}
                    <X size={13} aria-hidden="true" />
                  </button>
                ))}
              </div>
            ) : null}
            {hasOwnershipLabels && preferences.ownershipType !== "all" ? <p className="control-note">Ownership filter: {ownershipLabel(preferences.ownershipType)}</p> : null}
          </div>
          <label className="wide">
            <span>Search</span>
            <input
              value={preferences.query}
              onChange={(event) => onChange("query", event.currentTarget.value)}
              placeholder="School, city, state"
              aria-label="Search schools"
            />
          </label>
        </>
      ) : null}
      <details className="wide weight-panel">
        <summary>Scoring weights</summary>
        <div className="preset-row" aria-label="Scoring presets">
          {liveWeightPresets.map((preset) => (
            <button className="action-button" type="button" key={preset.id} onClick={() => applyPreset(preset)}>
              {preset.label}
            </button>
          ))}
          <button className="action-button" type="button" onClick={() => onChange("liveWeights", defaultLiveWeights)}>
            <RotateCcw size={15} aria-hidden="true" />
            Reset weights
          </button>
        </div>
        <div className="weight-list">
          {weightOrder.map((key) => (
            <label className="weight-control" key={key}>
              <span>
                {weightLabel(key)}
                <strong>{preferences.liveWeights[key]}</strong>
              </span>
              <input
                type="range"
                min="0"
                max="50"
                step="5"
                value={preferences.liveWeights[key]}
                onChange={(event) => updateWeight(key, Number(event.currentTarget.value))}
                aria-label={`${weightLabel(key)} weight`}
              />
              <small>{liveWeightDescriptions[key]}</small>
            </label>
          ))}
        </div>
      </details>
    </form>
  );
}

function weightLabel(key: LiveWeightKey): string {
  if (key === "mcatFit") return "MCAT fit";
  if (key === "gpaFit") return "GPA fit";
  if (key === "stateFit") return "State/residency fit";
  if (key === "costFit") return "Cost fit";
  return "Baseline attendance context";
}
