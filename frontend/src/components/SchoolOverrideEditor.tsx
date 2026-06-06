import { RotateCcw, SlidersHorizontal } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import {
  formatLiveScore,
  liveComponentMetadata,
  liveWeightOrder,
  mergeOverrideWeights,
  scoreSchoolWithOverride,
  type SchoolWeightOverride,
} from "../lib/live-scoring";
import type { LiveWeightKey, LiveWeights, PreferenceState, ProductSchool } from "../lib/school-utils";
import type { LocalSchoolState } from "./useLocalSchoolState";

type Props = {
  school: ProductSchool;
  schools: ProductSchool[];
  preferences: PreferenceState;
  local: LocalSchoolState;
  override?: SchoolWeightOverride | null;
};

export function SchoolOverrideEditor({ school, schools, preferences, local, override = null }: Props) {
  const [draftWeights, setDraftWeights] = useState<LiveWeights>(() => buildDraftWeights(preferences.liveWeights, override));
  const validationError = validateWeights(draftWeights);
  const previewOverride = useMemo<SchoolWeightOverride>(
    () => ({
      schoolSlug: school.slug,
      weights: draftWeights,
      updatedAt: override?.updatedAt || new Date().toISOString(),
    }),
    [draftWeights, override?.updatedAt, school.slug],
  );
  const preview = useMemo(() => scoreSchoolWithOverride(school, schools, preferences, previewOverride), [previewOverride, preferences, school, schools]);
  const adjustedScore = preview.adjustedScore;
  const componentRows = adjustedScore?.liveContributionRows || [];

  useEffect(() => {
    setDraftWeights(buildDraftWeights(preferences.liveWeights, override));
  }, [override?.updatedAt, preferences.liveWeights, school.slug]);

  function updateWeight(key: LiveWeightKey, value: string) {
    const nextValue = Number(value);
    setDraftWeights((current) => ({
      ...current,
      [key]: Number.isFinite(nextValue) ? nextValue : 0,
    }));
  }

  function applyOverride() {
    if (validationError) return;
    local.setSchoolWeightOverride(school.slug, draftWeights);
  }

  function resetToGlobal() {
    local.removeSchoolWeightOverride(school.slug);
    setDraftWeights(preferences.liveWeights);
  }

  return (
    <section className="override-editor" aria-label={`Personal scoring override for ${school.name}`}>
      <div className="override-editor-heading">
        <div>
          <p className="eyebrow">Personal scoring override</p>
          <h3>{school.name}</h3>
        </div>
        {override ? <span className="status-chip override">Override applied</span> : null}
      </div>

      <p className="scoring-copy">
        Overrides are stored in this browser only. The adjusted score changes this school&apos;s local scoring emphasis and keeps the global score visible.
      </p>
      {override ? <p className="state-notice">Override applied. Adjusted Score uses school-specific weights, so compare it alongside Global Score.</p> : null}

      <dl className="metric-strip override-preview">
        <div>
          <dt>Global Score</dt>
          <dd>{formatLiveScore(preview.globalScore.yourScore)}</dd>
        </div>
        <div>
          <dt>Preview Adjusted Score</dt>
          <dd>{formatLiveScore(adjustedScore?.yourScore ?? null)}</dd>
        </div>
        <div>
          <dt>Preview Coverage</dt>
          <dd>{adjustedScore ? `${adjustedScore.liveCoverage.label} (${adjustedScore.liveCoverage.available}/${adjustedScore.liveCoverage.possible})` : "Needs data"}</dd>
        </div>
      </dl>

      <div className="override-weight-list">
        {liveComponentMetadata.map((component) => {
          const row = componentRows.find((item) => item.componentKey === component.key);
          return (
            <label className="override-weight-control" key={component.key}>
              <span>
                <strong>{component.label}</strong>
                <small>Global {preferences.liveWeights[component.key]}</small>
              </span>
              <input
                aria-label={`${component.label} override weight`}
                type="number"
                min="0"
                max="100"
                step="1"
                value={draftWeights[component.key]}
                onChange={(event) => updateWeight(component.key, event.currentTarget.value)}
              />
              <small>
                Score {row?.scoreValue === null || row?.scoreValue === undefined ? "not included" : row.scoreValue.toFixed(1)} / Weight {draftWeights[component.key]} /{" "}
                {row?.included ? "included" : row?.reason || "not included"}
              </small>
            </label>
          );
        })}
      </div>

      {validationError ? (
        <p className="state-notice" role="alert">
          {validationError}
        </p>
      ) : null}

      <div className="card-actions override-actions">
        <button className="action-button strong" type="button" onClick={applyOverride} disabled={Boolean(validationError)}>
          <SlidersHorizontal size={16} aria-hidden="true" />
          Apply override
        </button>
        <button className="action-button" type="button" onClick={resetToGlobal}>
          <RotateCcw size={16} aria-hidden="true" />
          Reset to global
        </button>
      </div>
    </section>
  );
}

function buildDraftWeights(globalWeights: LiveWeights, override: SchoolWeightOverride | null | undefined): LiveWeights {
  return mergeOverrideWeights(globalWeights, override?.weights || {});
}

function validateWeights(weights: LiveWeights): string {
  for (const key of liveWeightOrder) {
    const value = weights[key];
    if (!Number.isFinite(value)) return "Weights must be finite numbers.";
    if (value < 0) return "Weights cannot be negative.";
    if (value > 100) return "Weights must be 100 or less.";
  }
  if (liveWeightOrder.every((key) => weights[key] === 0)) return "At least one override weight must be above 0.";
  return "";
}
