import { useEffect, useMemo, useState } from "react";
import type { ReactNode } from "react";
import {
  formatLiveScore,
  formatRank,
  liveComponentMetadata,
  liveWeightOrder,
  liveWeightPresets,
  scoreSchools,
  type LiveContributionRow,
  type LiveSchoolScore,
} from "../lib/live-scoring";
import type { PreferenceState, ProductSchool } from "../lib/school-utils";
import { cityLabelFromKey, filterSchools, ownershipLabel, schoolsHaveOwnershipLabels, stateLabel } from "../lib/school-utils";
import { PreferenceControls } from "./PreferenceControls";
import { useLocalSchoolState } from "./useLocalSchoolState";

type Props = {
  schools: ProductSchool[];
  caveat: string;
};

type AssumptionRow = {
  assumption: string;
  currentValue: string;
  usedBy: string;
  canChange: string;
  source: string;
  notes: string;
};

const SELECTED_SCHOOL_KEY = "msr.product.scoring.selectedSchool.v1";

const presetGuidance: Record<string, { bestFor: string; limitations: string }> = {
  balanced: {
    bestFor: "Broad first-pass review.",
    limitations: "Still a deterministic score-screen fit, not admissions probability.",
  },
  "cost-aware": {
    bestFor: "Prioritizing listed cost context.",
    limitations: "Does not know actual scholarships.",
  },
  "academic-screen": {
    bestFor: "Emphasizing MCAT/GPA screen fit.",
    limitations: "Still not admissions probability.",
  },
  "florida-first": {
    bestFor: "Testing a Florida home-state lens.",
    limitations: "Prioritizes state context but does not guarantee in-state preference.",
  },
  "state-first": {
    bestFor: "Testing a stronger residency lens.",
    limitations: "Generated OOS context can still be partial.",
  },
};

export function ScoringAssumptionsApp({ schools, caveat }: Props) {
  const local = useLocalSchoolState();
  const [selectedSlug, setSelectedSlug] = useState("");
  const hasOwnershipLabels = schoolsHaveOwnershipLabels(schools);
  const mdPreferences: PreferenceState = useMemo(() => ({ ...local.preferences, degree: "MD" }), [local.preferences]);
  const eligibleMdSchools = useMemo(
    () => filterSchools(schools, mdPreferences).filter((school) => school.degree === "MD" && !local.notInterested.includes(school.slug)),
    [schools, mdPreferences, local.notInterested],
  );
  const scoredSchools = useMemo(() => scoreSchools(eligibleMdSchools, mdPreferences), [eligibleMdSchools, mdPreferences]);
  const defaultScore = scoredSchools.find((score) => score.yourRank !== null) || scoredSchools[0] || null;
  const selectedScore = scoredSchools.find((score) => score.school.slug === selectedSlug) || defaultScore;
  const activePreset = findActivePreset(local.preferences);
  const allWeightsZero = liveWeightOrder.every((key) => local.preferences.liveWeights[key] === 0);
  const assumptionRows = buildAssumptionRows(local.preferences, local.notInterested.length, hasOwnershipLabels, activePreset);
  const movementRows = scoredSchools.slice(0, 25);

  useEffect(() => {
    try {
      const stored = window.localStorage.getItem(SELECTED_SCHOOL_KEY);
      if (stored) setSelectedSlug(stored);
    } catch {
      setSelectedSlug("");
    }
  }, []);

  useEffect(() => {
    if (!selectedScore) return;
    if (!selectedSlug || !scoredSchools.some((score) => score.school.slug === selectedSlug)) {
      setSelectedSlug(selectedScore.school.slug);
    }
  }, [scoredSchools, selectedScore, selectedSlug]);

  function updateSelectedSchool(slug: string) {
    setSelectedSlug(slug);
    try {
      window.localStorage.setItem(SELECTED_SCHOOL_KEY, slug);
    } catch {
      // Local persistence is optional; scoring still works without it.
    }
  }

  return (
    <div className="scoring-workspace">
      <aside className="builder-panel scoring-controls" aria-label="Scoring inputs">
        <div className="panel-heading">
          <p className="eyebrow">Browser-local controls</p>
          <h2>Adjust assumptions</h2>
        </div>
        <PreferenceControls schools={schools} preferences={local.preferences} onChange={local.updatePreference} mode="scoring" />
        <p className="panel-note">{caveat}</p>
        <p className="panel-note">This Scoring page covers MD schools only. DO schools need a separate scoring flow because the source context and applicant-pool assumptions differ.</p>
        <p className="panel-note">Your inputs are stored in this browser only. They are not sent to a server by this static site.</p>
      </aside>

      <section className="scoring-main" aria-label="Scoring assumptions workspace">
        <div className="feed-heading">
          <div>
            <p className="eyebrow">Scoring workspace</p>
            <h2>Current fit ranking audit</h2>
            <p>MD schools only. Weighted points use present components only; missing values are not treated as zero.</p>
          </div>
          <div className="count-block" aria-label="Eligible MD schools">
            <strong>{scoredSchools.length}</strong>
            <span>eligible MD schools</span>
          </div>
        </div>

        {allWeightsZero ? (
          <div className="state-notice" role="status">
            Scoring is disabled because all component weights are 0. Increase at least one weight to restore Your Score and Your Rank.
          </div>
        ) : null}

        <section className="scoring-section" aria-labelledby="assumptions-heading">
          <div className="section-heading">
            <div>
              <p className="eyebrow">Assumptions</p>
              <h2 id="assumptions-heading">Assumptions in use</h2>
            </div>
            <span className="status-chip neutral">Scoring universe: MD schools only</span>
          </div>
          <ResponsiveTable>
            <thead>
              <tr>
                <th>Assumption</th>
                <th>Current value</th>
                <th>Used by</th>
                <th>Can change?</th>
                <th>Source</th>
                <th>Notes</th>
              </tr>
            </thead>
            <tbody>
              {assumptionRows.map((row) => (
                <tr key={row.assumption}>
                  <td data-label="Assumption">{row.assumption}</td>
                  <td data-label="Current value">{row.currentValue}</td>
                  <td data-label="Used by">{row.usedBy}</td>
                  <td data-label="Can change?">{row.canChange}</td>
                  <td data-label="Source">{row.source}</td>
                  <td data-label="Notes">{row.notes}</td>
                </tr>
              ))}
            </tbody>
          </ResponsiveTable>
        </section>

        <section className="scoring-section" aria-labelledby="weights-heading">
          <div className="section-heading">
            <div>
              <p className="eyebrow">Weights</p>
              <h2 id="weights-heading">Weights and formulas</h2>
            </div>
            <span className="status-chip neutral">Denominator basis: present components only</span>
          </div>
          <p className="scoring-copy">
            A component with weight 0 stays visible as Not included: weight is 0. If all weights are 0, scoring is disabled instead of falling back to default weights.
          </p>
          <ResponsiveTable>
            <thead>
              <tr>
                <th>Component</th>
                <th>Formula</th>
                <th>Current weight</th>
                <th>When missing</th>
                <th>What a high score means</th>
              </tr>
            </thead>
            <tbody>
              {liveComponentMetadata.map((component) => (
                <tr key={component.key}>
                  <td data-label="Component">{component.label}</td>
                  <td data-label="Formula">{component.formulaLabel}</td>
                  <td data-label="Current weight">{formatWeight(local.preferences.liveWeights[component.key])}</td>
                  <td data-label="When missing">
                    {local.preferences.liveWeights[component.key] === 0 ? "Not included because weight is 0." : component.missingPolicy}
                  </td>
                  <td data-label="What a high score means">{component.highScoreMeans}</td>
                </tr>
              ))}
            </tbody>
          </ResponsiveTable>
        </section>

        <section className="scoring-section" aria-labelledby="preset-heading">
          <div className="section-heading">
            <div>
              <p className="eyebrow">Presets</p>
              <h2 id="preset-heading">Scenario and weight presets</h2>
            </div>
            <span className="status-chip neutral">Active scoring preset: {activePreset}</span>
          </div>
          <ResponsiveTable>
            <thead>
              <tr>
                <th>Preset</th>
                <th>MCAT</th>
                <th>GPA</th>
                <th>State/residency</th>
                <th>Cost</th>
                <th>Generated school context status</th>
                <th>Generated school context weight</th>
                <th>Best for</th>
                <th>Limitations</th>
              </tr>
            </thead>
            <tbody>
              {liveWeightPresets.map((preset) => {
                const guidance = presetGuidance[preset.id];
                return (
                  <tr key={preset.id}>
                    <td data-label="Preset">{preset.label}</td>
                    <td data-label="MCAT">{preset.weights.mcatFit}</td>
                    <td data-label="GPA">{preset.weights.gpaFit}</td>
                    <td data-label="State/residency">{preset.weights.stateFit}</td>
                    <td data-label="Cost">{preset.weights.costFit}</td>
                    <td data-label="Generated school context status">{preset.weights.baselineAttendance > 0 ? "Included" : "Not included because weight is 0."}</td>
                    <td data-label="Generated school context weight">{preset.weights.baselineAttendance}</td>
                    <td data-label="Best for">{guidance?.bestFor || "Testing a deterministic value lens."}</td>
                    <td data-label="Limitations">{guidance?.limitations || "Generated school context is experimental and can be set to weight 0."}</td>
                  </tr>
                );
              })}
            </tbody>
          </ResponsiveTable>
        </section>

        <section className="scoring-section" aria-labelledby="breakdown-heading">
          <div className="section-heading">
            <div>
              <p className="eyebrow">Selected school</p>
              <h2 id="breakdown-heading">School score breakdown</h2>
            </div>
            <label className="inline-picker">
              <span>Selected MD school</span>
              <select value={selectedScore?.school.slug || ""} onChange={(event) => updateSelectedSchool(event.currentTarget.value)}>
                {scoredSchools.map((score) => (
                  <option value={score.school.slug} key={score.school.slug}>
                    {score.school.name}
                  </option>
                ))}
              </select>
            </label>
          </div>

          {selectedScore ? (
            <>
              <ScoreSummary score={selectedScore} />
              <p className="scoring-copy">Weighted points use present components only. Missing values are not treated as zero.</p>
              <ResponsiveTable>
                <thead>
                  <tr>
                    <th>Component</th>
                    <th>Applicant input</th>
                    <th>School value</th>
                    <th>Formula</th>
                    <th>Score</th>
                    <th>Weight</th>
                    <th>Weighted points</th>
                    <th>Included?</th>
                    <th>Reason</th>
                  </tr>
                </thead>
                <tbody>
                  {selectedScore.liveContributionRows.map((row) => (
                    <tr key={row.componentKey}>
                      <td data-label="Component">{row.componentLabel}</td>
                      <td data-label="Applicant input">{row.applicantValueLabel}</td>
                      <td data-label="School value">{row.schoolValueLabel}</td>
                      <td data-label="Formula">{row.formulaLabel}</td>
                      <td data-label="Score">{row.scoreValue === null ? "Not included" : row.scoreValue.toFixed(1)}</td>
                      <td data-label="Weight">{formatWeight(row.weight)}</td>
                      <td data-label="Weighted points">{row.weightedPoints === null ? "Not included" : row.weightedPoints.toFixed(1)}</td>
                      <td data-label="Included?">{row.included ? "Included" : row.reason === "Not included: weight is 0" ? "Not included: weight is 0" : "Not included"}</td>
                      <td data-label="Reason">{row.reason}</td>
                    </tr>
                  ))}
                </tbody>
              </ResponsiveTable>
            </>
          ) : (
            <div className="empty-state">
              <h2>No eligible MD schools</h2>
              <p>Clear exclusions or Not Interested selections to restore MD schools to the scoring workspace.</p>
            </div>
          )}
        </section>

        <section className="scoring-section" aria-labelledby="movement-heading">
          <div className="section-heading">
            <div>
              <p className="eyebrow">Rank audit</p>
              <h2 id="movement-heading">Rank movement</h2>
            </div>
            <span className="status-chip neutral">Top {movementRows.length} currently eligible MD schools</span>
          </div>
          <ResponsiveTable>
            <thead>
              <tr>
                <th>School</th>
                <th>Your Rank</th>
                <th>Baseline Rank</th>
                <th>Rank movement</th>
                <th>Your Score</th>
                <th>Coverage</th>
                <th>Why did this move?</th>
                <th>Missing pieces</th>
              </tr>
            </thead>
            <tbody>
              {movementRows.map((score) => (
                <tr key={score.school.slug}>
                  <td data-label="School">{score.school.name}</td>
                  <td data-label="Your Rank">{formatRank(score.yourRank)}</td>
                  <td data-label="Baseline Rank">{formatRank(score.baselineRank)}</td>
                  <td data-label="Rank movement">{formatRankMovement(score)}</td>
                  <td data-label="Your Score">{formatLiveScore(score.yourScore)}</td>
                  <td data-label="Coverage">
                    {score.liveCoverage.label} ({score.liveCoverage.available}/{score.liveCoverage.possible})
                  </td>
                  <td data-label="Why did this move?">{whyDidMove(score)}</td>
                  <td data-label="Missing pieces">{missingPieces(score.liveContributionRows)}</td>
                </tr>
              ))}
            </tbody>
          </ResponsiveTable>
        </section>
      </section>
    </div>
  );
}

function ResponsiveTable({ children }: { children: ReactNode }) {
  return (
    <div className="responsive-table" role="region" tabIndex={0}>
      <table>{children}</table>
    </div>
  );
}

function ScoreSummary({ score }: { score: LiveSchoolScore }) {
  return (
    <dl className="metric-strip scoring-summary">
      <div>
        <dt>School name</dt>
        <dd>{score.school.name}</dd>
      </div>
      <div>
        <dt>Location</dt>
        <dd>
          {score.school.city || "City not listed"}, {score.school.stateAbbrev || score.school.state || "State not listed"}
        </dd>
      </div>
      <div>
        <dt>Degree</dt>
        <dd>{score.school.degree || "Not listed"}</dd>
      </div>
      <div>
        <dt>Your Rank</dt>
        <dd>{formatRank(score.yourRank)}</dd>
      </div>
      <div>
        <dt>Baseline Rank</dt>
        <dd>{formatRank(score.baselineRank)}</dd>
      </div>
      <div>
        <dt>Your Score</dt>
        <dd>{formatLiveScore(score.yourScore)}</dd>
      </div>
      <div>
        <dt>Coverage</dt>
        <dd>
          {score.liveCoverage.label} ({score.liveCoverage.available}/{score.liveCoverage.possible})
        </dd>
      </div>
    </dl>
  );
}

function buildAssumptionRows(preferences: PreferenceState, notInterestedCount: number, hasOwnershipLabels: boolean, activePreset: string): AssumptionRow[] {
  const excludedStates = preferences.excludedStates.length ? preferences.excludedStates.map((state) => stateLabel(state)).join(", ") : "None";
  const excludedCities = preferences.excludedCities.length ? preferences.excludedCities.map((city) => cityLabelFromKey(city)).join(", ") : "None";
  const ownershipStatus = hasOwnershipLabels ? ownershipLabel(preferences.ownershipType) : "Unknown / disabled";
  const applicantMcat = preferences.mcat.trim() || "Not entered";
  const applicantGpa = preferences.gpa.trim() || "Not entered";
  const homeState = preferences.homeState ? stateLabel(preferences.homeState) : "Not entered";
  const missingMcatNote = preferences.mcat.trim() ? "Used when school MCAT data is available." : "This component is excluded from Your Score until entered.";
  const missingGpaNote = preferences.gpa.trim() ? "Used when school GPA data is available." : "This component is excluded from Your Score until entered.";
  const missingStateNote = preferences.homeState ? "Used for same-state and OOS context scoring." : "This component is excluded from Your Score until entered.";
  const rows: AssumptionRow[] = [
    {
      assumption: "Applicant MCAT",
      currentValue: applicantMcat,
      usedBy: "MCAT fit",
      canChange: "Yes",
      source: "Browser-local input",
      notes: missingMcatNote,
    },
    {
      assumption: "Applicant GPA",
      currentValue: applicantGpa,
      usedBy: "GPA fit",
      canChange: "Yes",
      source: "Browser-local input",
      notes: missingGpaNote,
    },
    {
      assumption: "Home state",
      currentValue: homeState,
      usedBy: "State/residency fit and cost fit",
      canChange: "Yes",
      source: "Browser-local input",
      notes: missingStateNote,
    },
    {
      assumption: "Scoring universe",
      currentValue: "MD schools only",
      usedBy: "Selected-school and rank movement tables",
      canChange: "No in this slice",
      source: "Scoring workspace scope",
      notes: "DO schools use a different source context and are planned for a separate scoring flow.",
    },
    {
      assumption: "Cost basis",
      currentValue: "Home-state-aware positive listed cost",
      usedBy: "Cost fit",
      canChange: "Indirectly through home state",
      source: "Generated payload cost and tuition fields",
      notes: "Zero, blank, negative, or unparsable cost values are missing; one positive listed cost may be used as a single listed cost fallback.",
    },
    {
      assumption: "Region filter",
      currentValue: regionLabel(preferences.region),
      usedBy: "Eligible MD school set",
      canChange: "Yes",
      source: "Browser-local filter",
      notes: "This filter changes which MD schools appear in the score tables.",
    },
    {
      assumption: "Cost data filter",
      currentValue: costFilterLabel(preferences.cost),
      usedBy: "Eligible MD school set",
      canChange: "Yes",
      source: "Browser-local filter",
      notes: "This filter controls school eligibility; cost fit still uses positive applicable listed cost values.",
    },
    {
      assumption: "Excluded states",
      currentValue: excludedStates,
      usedBy: "Eligible MD school set",
      canChange: "Yes",
      source: "Browser-local exclusions",
      notes: "Excluded schools do not appear in this scoring workspace.",
    },
    {
      assumption: "Excluded cities",
      currentValue: excludedCities,
      usedBy: "Eligible MD school set",
      canChange: "Yes",
      source: "Browser-local exclusions",
      notes: "Excluded schools do not appear in this scoring workspace.",
    },
    {
      assumption: "Score-screen fit filter",
      currentValue: fitFilterLabel(preferences.fit),
      usedBy: "Eligible MD school set",
      canChange: "Yes",
      source: "Browser-local filter",
      notes: "This filter changes eligibility only; it does not create an admissions probability.",
    },
    {
      assumption: "Search filter",
      currentValue: preferences.query.trim() || "None",
      usedBy: "Eligible MD school set",
      canChange: "Yes",
      source: "Browser-local filter",
      notes: "Search narrows the schools shown in this workspace.",
    },
    {
      assumption: "Institution ownership filter status",
      currentValue: ownershipStatus,
      usedBy: "Eligible MD school set",
      canChange: hasOwnershipLabels ? "Yes" : "No",
      source: hasOwnershipLabels ? "Source-backed ownership labels" : "Payload has no source-backed ownership labels",
      notes: hasOwnershipLabels ? "Only source-backed labels are used." : "The app is not inferring public or private status from names.",
    },
    {
      assumption: "Not Interested behavior",
      currentValue: `${notInterestedCount} hidden locally`,
      usedBy: "Eligible MD school set",
      canChange: "Yes, from school cards and local lists",
      source: "Browser-local list state",
      notes: "Not Interested schools are removed from this scoring workspace until restored.",
    },
    {
      assumption: "Active scoring preset",
      currentValue: activePreset,
      usedBy: "All live components",
      canChange: "Yes",
      source: "Browser-local weights",
      notes: "Custom weights are allowed; negative weights are not allowed.",
    },
  ];

  for (const component of liveComponentMetadata) {
    const weight = preferences.liveWeights[component.key];
    rows.push({
      assumption: `${component.label} weight`,
      currentValue: formatWeight(weight),
      usedBy: component.label,
      canChange: "Yes",
      source: "Browser-local weights",
      notes: weight === 0 ? "Not included because weight is 0." : "Included when the component data is present.",
    });
  }

  return rows;
}

function regionLabel(value: string): string {
  return value === "all" ? "All regions" : value;
}

function costFilterLabel(value: PreferenceState["cost"]): string {
  if (value === "has-cost") return "Has cost data";
  if (value === "lower-cost") return "Lower listed cost first";
  return "Any cost data";
}

function fitFilterLabel(value: PreferenceState["fit"]): string {
  if (value === "within") return "Within published range";
  if (value === "near") return "Near published range";
  if (value === "below") return "Below published range";
  if (value === "above") return "Above published range";
  if (value === "needs-inputs") return "Needs inputs or data";
  return "All";
}

function findActivePreset(preferences: PreferenceState): string {
  const preset = liveWeightPresets.find((item) => {
    const weightsMatch = liveWeightOrder.every((key) => item.weights[key] === preferences.liveWeights[key]);
    const stateMatches = item.homeState ? item.homeState === preferences.homeState : true;
    return weightsMatch && stateMatches;
  });
  return preset ? preset.label : "Custom weights";
}

function formatWeight(value: number): string {
  return value === 0 ? "0 (Not included because weight is 0.)" : String(value);
}

function formatRankMovement(score: LiveSchoolScore): string {
  if (score.yourRank === null) return "Unranked";
  if (score.baselineRank === null) return "Baseline unavailable";
  const delta = score.yourRank - score.baselineRank;
  if (delta === 0) return "Unchanged";
  return delta < 0 ? `Moved up ${Math.abs(delta)}` : `Moved down ${delta}`;
}

function whyDidMove(score: LiveSchoolScore): string {
  if (score.scoringDisabled) return score.scoringDisabledReason;
  if (score.yourRank === null) return "Needs at least one present weighted component.";
  if (score.baselineRank === null) return "Baseline Rank unavailable; live order uses available weighted components.";
  const delta = score.yourRank - score.baselineRank;
  if (Math.abs(delta) <= 1) return "No meaningful movement from baseline.";
  if (delta < 0) {
    const driver = strongestIncludedRow(score.liveContributionRows);
    return driver ? `Largest positive contribution: ${driver.componentLabel} (${driver.weightedPoints?.toFixed(1)} weighted points).` : "Moved up on available weighted components.";
  }

  const missing = firstMissingRow(score.liveContributionRows);
  if (missing) return `Missing from score: ${missing.componentLabel}.`;
  const lowest = weakestIncludedRow(score.liveContributionRows);
  return lowest ? `Lowest weighted contribution: ${lowest.componentLabel} (${lowest.weightedPoints?.toFixed(1)} weighted points).` : "Moved down on available weighted components.";
}

function strongestIncludedRow(rows: LiveContributionRow[]): LiveContributionRow | null {
  return includedRows(rows).sort((a, b) => (b.weightedPoints || 0) - (a.weightedPoints || 0))[0] || null;
}

function weakestIncludedRow(rows: LiveContributionRow[]): LiveContributionRow | null {
  return includedRows(rows).sort((a, b) => (a.weightedPoints || 0) - (b.weightedPoints || 0))[0] || null;
}

function firstMissingRow(rows: LiveContributionRow[]): LiveContributionRow | null {
  return rows.find((row) => row.notIncludedReasonType === "missing_data") || null;
}

function includedRows(rows: LiveContributionRow[]): LiveContributionRow[] {
  return rows.filter((row) => row.included && row.weightedPoints !== null);
}

function missingPieces(rows: LiveContributionRow[]): string {
  const missing = rows.filter((row) => row.notIncludedReasonType === "missing_data").map((row) => row.componentLabel);
  return missing.length ? missing.join(", ") : "None";
}
