import type { LiveWeightKey, LiveWeights, PreferenceState, ProductSchool } from "./school-utils";
import { toNumberOrNull, toPositiveNumberOrNull } from "./school-utils";

type ContributionEffect = "helps" | "hurts" | "neutral";
type CoverageLabel = "full" | "partial" | "limited" | "none";
export type LiveComponentGroup = "admissions" | "attendance";
export type LiveNotIncludedReasonType = "missing_data" | "zero_weight";

export type LiveContribution = {
  key: LiveWeightKey;
  label: string;
  value: number;
  weight: number;
  effect: ContributionEffect;
  detail: string;
};

export type LiveContributionRow = {
  componentKey: LiveWeightKey;
  componentLabel: string;
  componentGroup: LiveComponentGroup;
  applicantValueLabel: string;
  schoolValueLabel: string;
  formulaLabel: string;
  scoreValue: number | null;
  weight: number;
  presentWeightSum: number;
  weightedPoints: number | null;
  included: boolean;
  notIncludedReasonType: LiveNotIncludedReasonType | null;
  reason: string;
  sourceLabel: string;
  confidenceLabel: string;
};

export type LiveCoverage = {
  available: number;
  possible: number;
  percent: number;
  label: CoverageLabel;
};

export type LiveSchoolScore = {
  school: ProductSchool;
  baselineRank: number | null;
  baselineScore: number | null;
  yourRank: number | null;
  yourScore: number | null;
  liveAdmissionsScore: number | null;
  liveAttendanceScore: number | null;
  liveCoverage: LiveCoverage;
  liveContributions: LiveContribution[];
  liveContributionRows: LiveContributionRow[];
  liveWarnings: string[];
  scoringDisabled: boolean;
  scoringDisabledReason: string;
};

export type SchoolWeightOverride = {
  schoolSlug: string;
  weights: Partial<LiveWeights>;
  updatedAt: string;
};

export type SchoolAdjustedScore = {
  slug: string;
  globalScore: LiveSchoolScore;
  adjustedScore: LiveSchoolScore | null;
  overrideApplied: boolean;
  adjustedRank: number | null;
};

type ComponentResult = {
  key: LiveWeightKey;
  group: LiveComponentGroup;
  label: string;
  value: number | null;
  detail: string;
  warning: string;
  applicantValueLabel: string;
  schoolValueLabel: string;
  formulaLabel: string;
  sourceLabel: string;
  confidenceLabel: string;
};

export const liveWeightPresets: Array<{ id: string; label: string; weights: LiveWeights; homeState?: string }> = [
  {
    id: "balanced",
    label: "Balanced",
    weights: { mcatFit: 25, gpaFit: 25, stateFit: 20, costFit: 15, baselineAttendance: 15 },
  },
  {
    id: "cost-aware",
    label: "Cost-aware",
    weights: { mcatFit: 20, gpaFit: 20, stateFit: 15, costFit: 30, baselineAttendance: 15 },
  },
  {
    id: "academic-screen",
    label: "Academic-screen focused",
    weights: { mcatFit: 35, gpaFit: 35, stateFit: 15, costFit: 5, baselineAttendance: 10 },
  },
  {
    id: "florida-first",
    label: "Florida-first",
    weights: { mcatFit: 20, gpaFit: 20, stateFit: 30, costFit: 15, baselineAttendance: 15 },
    homeState: "FL",
  },
  {
    id: "state-first",
    label: "State-first",
    weights: { mcatFit: 20, gpaFit: 20, stateFit: 35, costFit: 10, baselineAttendance: 15 },
  },
];

export const liveWeightDescriptions: Record<LiveWeightKey, string> = {
  mcatFit: "Compares applicant MCAT with the school MCAT value when available.",
  gpaFit: "Compares applicant GPA with the school GPA value when available.",
  stateFit: "Rewards in-state schools and uses generated OOS context when available.",
  costFit: "Scores the applicable listed cost against other available costs.",
  baselineAttendance: "Uses generated school context from the existing payload.",
};

export type LiveComponentMetadata = {
  key: LiveWeightKey;
  label: string;
  group: LiveComponentGroup;
  formulaLabel: string;
  missingPolicy: string;
  highScoreMeans: string;
};

export const liveComponentMetadata: LiveComponentMetadata[] = [
  {
    key: "mcatFit",
    label: "MCAT fit",
    group: "admissions",
    formulaLabel: "7 + (applicant MCAT - school MCAT) / 2",
    missingPolicy: "Excluded from Your Score until applicant MCAT and school MCAT are available.",
    highScoreMeans: "Applicant MCAT is at or above this school's listed MCAT context.",
  },
  {
    key: "gpaFit",
    label: "GPA fit",
    group: "admissions",
    formulaLabel: "7 + (applicant GPA - school GPA) / 0.08",
    missingPolicy: "Excluded from Your Score until applicant GPA and school GPA are available.",
    highScoreMeans: "Applicant GPA is at or above this school's listed GPA context.",
  },
  {
    key: "stateFit",
    label: "State/residency fit",
    group: "admissions",
    formulaLabel: "Same state or source-backed OOS context",
    missingPolicy: "Excluded from Your Score until home state and state/OOS context are available.",
    highScoreMeans: "The school is in the selected home state or has stronger generated OOS context.",
  },
  {
    key: "costFit",
    label: "Cost fit",
    group: "attendance",
    formulaLabel: "Lowest applicable cost = 10, highest = 1",
    missingPolicy: "Excluded from Your Score when no positive applicable listed cost is available.",
    highScoreMeans: "The applicable listed cost is lower than other eligible schools in the current score set.",
  },
  {
    key: "baselineAttendance",
    label: "Generated school context",
    group: "attendance",
    formulaLabel: "Generated attendance context score",
    missingPolicy: "Excluded from Your Score when generated school context is unavailable.",
    highScoreMeans: "The generated payload contains stronger attendance context for this school.",
  },
];

export const liveWeightOrder: LiveWeightKey[] = liveComponentMetadata.map((component) => component.key);

const overrideWeightAliases: Record<string, LiveWeightKey> = {
  mcat: "mcatFit",
  mcatFit: "mcatFit",
  gpa: "gpaFit",
  gpaFit: "gpaFit",
  state: "stateFit",
  stateFit: "stateFit",
  cost: "costFit",
  costFit: "costFit",
  context: "baselineAttendance",
  baselineAttendance: "baselineAttendance",
};

export function scoreSchools(schools: ProductSchool[], preferences: PreferenceState): LiveSchoolScore[] {
  const costRange = buildCostRange(schools, preferences.homeState);
  const scored = schools.map((school) => scoreSchool(school, preferences, costRange));
  const hasLiveScores = scored.some((score) => score.yourScore !== null);
  const sorted = scored.sort((a, b) => compareLiveScores(a, b, hasLiveScores));

  if (!hasLiveScores) return sorted;
  return sorted.map((score, index) => ({
    ...score,
    yourRank: score.yourScore === null ? null : index + 1,
  }));
}

export function scoreSchoolWithOverride(
  school: ProductSchool,
  schools: ProductSchool[],
  globalPreferences: PreferenceState,
  override: SchoolWeightOverride | null | undefined,
): SchoolAdjustedScore {
  const costRange = buildCostRange(schools, globalPreferences.homeState);
  const globalScores = scoreSchools(schools, globalPreferences);
  const globalScore = globalScores.find((score) => score.school.slug === school.slug) || scoreSchool(school, globalPreferences, costRange);
  if (!override) {
    return {
      slug: school.slug,
      globalScore,
      adjustedScore: null,
      overrideApplied: false,
      adjustedRank: null,
    };
  }

  const adjustedPreferences: PreferenceState = {
    ...globalPreferences,
    liveWeights: mergeOverrideWeights(globalPreferences.liveWeights, override.weights),
  };
  const adjustedScore = scoreSchool(school, adjustedPreferences, costRange);

  return {
    slug: school.slug,
    globalScore,
    adjustedScore,
    overrideApplied: true,
    adjustedRank: null,
  };
}

export function scoreSchoolsWithOverrides(
  schools: ProductSchool[],
  globalPreferences: PreferenceState,
  overrides: Record<string, SchoolWeightOverride>,
): SchoolAdjustedScore[] {
  const globalScores = scoreSchools(schools, globalPreferences);
  const globalBySlug = new Map(globalScores.map((score) => [score.school.slug, score]));
  const costRange = buildCostRange(schools, globalPreferences.homeState);
  const adjustedRows = schools.map((school) => {
    const globalScore = globalBySlug.get(school.slug) || scoreSchool(school, globalPreferences, costRange);
    const override = overrides[school.slug] || null;
    if (!override) {
      return {
        slug: school.slug,
        globalScore,
        adjustedScore: null,
        overrideApplied: false,
        adjustedRank: null,
      };
    }

    const adjustedPreferences: PreferenceState = {
      ...globalPreferences,
      liveWeights: mergeOverrideWeights(globalPreferences.liveWeights, override.weights),
    };
    const adjustedScore = scoreSchool(school, adjustedPreferences, costRange);
    return {
      slug: school.slug,
      globalScore,
      adjustedScore,
      overrideApplied: true,
      adjustedRank: null,
    };
  });

  if (!adjustedRows.some((row) => scoreValueForAdjustedRank(row) !== null)) return adjustedRows;

  const rankBySlug = new Map(
    [...adjustedRows]
      .sort(compareAdjustedRows)
      .map((row, index) => [row.slug, scoreValueForAdjustedRank(row) === null ? null : index + 1]),
  );

  return adjustedRows.map((row) => ({
    ...row,
    adjustedRank: row.overrideApplied ? rankBySlug.get(row.slug) ?? null : null,
  }));
}

export function normalizeOverrideWeights(value: unknown): Partial<LiveWeights> {
  if (!value || typeof value !== "object") return {};
  const source = value as Record<string, unknown>;
  const weights: Partial<LiveWeights> = {};
  for (const [key, targetKey] of Object.entries(overrideWeightAliases)) {
    if (!(key in source)) continue;
    const weight = Number(source[key]);
    if (Number.isFinite(weight) && weight >= 0 && weight <= 100) {
      weights[targetKey] = weight;
    }
  }
  return weights;
}

export function mergeOverrideWeights(globalWeights: LiveWeights, overrideWeights: Partial<LiveWeights>): LiveWeights {
  return {
    ...globalWeights,
    ...normalizeOverrideWeights(overrideWeights),
  };
}

export function formatLiveScore(value: number | null): string {
  return value === null ? "Needs data" : value.toFixed(1);
}

export function formatRank(value: number | null): string {
  return value === null ? "Unranked" : `#${value}`;
}

export function buildLiveFactorBullets(score: LiveSchoolScore): string[] {
  const bullets = score.liveContributions.slice(0, 4).map((contribution) => {
    const direction = contribution.effect === "helps" ? "helps" : contribution.effect === "hurts" ? "pulls down" : "is neutral for";
    return `${contribution.label} ${direction} this live rank (${contribution.value.toFixed(1)}/10). ${contribution.detail}.`;
  });

  for (const warning of score.liveWarnings.slice(0, 3)) {
    bullets.push(`Missing from live score: ${warning}`);
  }

  bullets.push(`Baseline Rank remains ${formatRank(score.baselineRank)} from generated data.`);
  return bullets.slice(0, 6);
}

function scoreSchool(school: ProductSchool, preferences: PreferenceState, costRange: CostRange): LiveSchoolScore {
  const weights = preferences.liveWeights;
  const components = buildComponents(school, preferences, costRange);
  const scoringDisabled = liveWeightOrder.every((key) => weights[key] === 0);
  const scoringDisabledReason = scoringDisabled ? "Scoring is disabled because all component weights are 0." : "";
  const activeComponents = components.filter((component) => weights[component.key] > 0);
  const liveContributions = activeComponents.flatMap((component) => {
    if (component.value === null) return [];
    return [
      {
        key: component.key,
        label: component.label,
        value: component.value,
        weight: weights[component.key],
        effect: effectFor(component.value),
        detail: component.detail,
      },
    ];
  });
  const liveWarnings = activeComponents.flatMap((component) => (component.value === null ? [component.warning] : []));
  const presentWeightSum = liveContributions.reduce((total, contribution) => total + weights[contribution.key], 0);
  const liveContributionRows = components.map((component) => buildContributionRow(component, weights, presentWeightSum));

  const yourScore = weightedAverage(liveContributions, weights);
  const liveAdmissionsScore = weightedAverage(
    liveContributions.filter((contribution) => components.find((component) => component.key === contribution.key)?.group === "admissions"),
    weights,
  );
  const liveAttendanceScore = weightedAverage(
    liveContributions.filter((contribution) => components.find((component) => component.key === contribution.key)?.group === "attendance"),
    weights,
  );

  return {
    school,
    baselineRank: school.decisionRank ?? school.overallRank,
    baselineScore: school.baselineScore,
    yourRank: null,
    yourScore,
    liveAdmissionsScore,
    liveAttendanceScore,
    liveCoverage: buildCoverage(liveContributions.length, activeComponents.length),
    liveContributions,
    liveContributionRows,
    liveWarnings,
    scoringDisabled,
    scoringDisabledReason,
  };
}

function buildComponents(school: ProductSchool, preferences: PreferenceState, costRange: CostRange): ComponentResult[] {
  return [
    buildMcatFit(school, preferences),
    buildGpaFit(school, preferences),
    buildStateFit(school, preferences),
    buildCostFit(school, preferences, costRange),
    buildBaselineAttendance(school),
  ];
}

function buildMcatFit(school: ProductSchool, preferences: PreferenceState): ComponentResult {
  const applicantMcat = toNumberOrNull(preferences.mcat);
  const schoolMcat = toNumberOrNull(school.schoolMcat);
  if (applicantMcat === null || schoolMcat === null) {
    return missingComponent(
      "mcatFit",
      "admissions",
      "MCAT fit",
      "applicant MCAT or school MCAT is unavailable, so MCAT is excluded from the denominator.",
      applicantMcat === null ? "Not entered" : String(applicantMcat),
      schoolMcat === null ? "Not available" : String(schoolMcat),
      "7 + (applicant MCAT - school MCAT) / 2",
      school.statsSource || "School MCAT field",
      school.statsQuality || school.dataConfidence || "Not available",
    );
  }
  return {
    key: "mcatFit",
    group: "admissions",
    label: "MCAT fit",
    value: clampScore(7 + (applicantMcat - schoolMcat) / 2),
    detail: `Applicant MCAT ${applicantMcat} compared with school MCAT ${schoolMcat}`,
    warning: "",
    applicantValueLabel: String(applicantMcat),
    schoolValueLabel: String(schoolMcat),
    formulaLabel: "7 + (applicant MCAT - school MCAT) / 2",
    sourceLabel: school.statsSource || "School MCAT field",
    confidenceLabel: school.statsQuality || school.dataConfidence || "Not available",
  };
}

function buildGpaFit(school: ProductSchool, preferences: PreferenceState): ComponentResult {
  const applicantGpa = toNumberOrNull(preferences.gpa);
  const schoolGpa = toNumberOrNull(school.schoolGpa);
  if (applicantGpa === null || schoolGpa === null) {
    return missingComponent(
      "gpaFit",
      "admissions",
      "GPA fit",
      "applicant GPA or school GPA is unavailable, so GPA is excluded from the denominator.",
      applicantGpa === null ? "Not entered" : applicantGpa.toFixed(2),
      schoolGpa === null ? "Not available" : schoolGpa.toFixed(2),
      "7 + (applicant GPA - school GPA) / 0.08",
      school.statsSource || "School GPA field",
      school.statsQuality || school.dataConfidence || "Not available",
    );
  }
  return {
    key: "gpaFit",
    group: "admissions",
    label: "GPA fit",
    value: clampScore(7 + (applicantGpa - schoolGpa) / 0.08),
    detail: `Applicant GPA ${applicantGpa.toFixed(2)} compared with school GPA ${schoolGpa.toFixed(2)}`,
    warning: "",
    applicantValueLabel: applicantGpa.toFixed(2),
    schoolValueLabel: schoolGpa.toFixed(2),
    formulaLabel: "7 + (applicant GPA - school GPA) / 0.08",
    sourceLabel: school.statsSource || "School GPA field",
    confidenceLabel: school.statsQuality || school.dataConfidence || "Not available",
  };
}

function buildStateFit(school: ProductSchool, preferences: PreferenceState): ComponentResult {
  const homeState = preferences.homeState;
  if (!homeState) {
    return missingComponent(
      "stateFit",
      "admissions",
      "State/residency fit",
      "home state is not selected, so state/residency fit is excluded from the denominator.",
      "Not entered",
      school.stateAbbrev || school.state || "Not available",
      "Same state or source-backed OOS context",
      "School state and generated OOS context",
      school.dataConfidence || "Not available",
    );
  }
  if (school.stateAbbrev === homeState) {
    return {
      key: "stateFit",
      group: "admissions",
      label: "State/residency fit",
      value: 10,
      detail: `${school.stateAbbrev} matches selected home state ${homeState}`,
      warning: "",
      applicantValueLabel: homeState,
      schoolValueLabel: school.stateAbbrev || school.state || "Not available",
      formulaLabel: "Same state or source-backed OOS context",
      sourceLabel: "School state",
      confidenceLabel: school.dataConfidence || "Not available",
    };
  }
  if (school.oosFriendlinessScore !== null) {
    return {
      key: "stateFit",
      group: "admissions",
      label: "State/residency fit",
      value: clampScore(school.oosFriendlinessScore),
      detail: `Generated OOS context score is ${school.oosFriendlinessScore.toFixed(1)}`,
      warning: "",
      applicantValueLabel: homeState,
      schoolValueLabel: `${school.stateAbbrev || school.state || "Out of state"}; OOS context ${school.oosFriendlinessScore.toFixed(1)}`,
      formulaLabel: "Same state or source-backed OOS context",
      sourceLabel: "Generated OOS context",
      confidenceLabel: school.dataConfidence || "Not available",
    };
  }
  return missingComponent(
    "stateFit",
    "admissions",
    "State/residency fit",
    "OOS context is unavailable for this school, so state/residency fit is excluded from the denominator.",
    homeState,
    school.stateAbbrev || school.state || "Not available",
    "Same state or source-backed OOS context",
    "Generated OOS context",
    school.dataConfidence || "Not available",
  );
}

function buildCostFit(school: ProductSchool, preferences: PreferenceState, costRange: CostRange): ComponentResult {
  const cost = applicableCost(school, preferences.homeState);
  if (cost.value === null || costRange.min === null || costRange.max === null) {
    return missingComponent(
      "costFit",
      "attendance",
      "Cost fit",
      "applicable cost data is unavailable, so cost is excluded from the denominator.",
      preferences.homeState ? `Home state ${preferences.homeState}` : "No home state selected",
      "Not available",
      "Lowest applicable cost = 10, highest = 1",
      "Cost and tuition fields",
      school.costConfidence || school.dataConfidence || "Not available",
    );
  }
  const value = costRange.max === costRange.min ? 10 : 10 - ((cost.value - costRange.min) / (costRange.max - costRange.min)) * 9;
  return {
    key: "costFit",
    group: "attendance",
    label: "Cost fit",
    value: clampScore(value),
    detail: `Applicable listed cost is ${formatDollars(cost.value)}. ${cost.detail}`,
    warning: "",
    applicantValueLabel: preferences.homeState ? `Home state ${preferences.homeState}` : "No home state selected",
    schoolValueLabel: formatDollars(cost.value),
    formulaLabel: "Lowest applicable cost = 10, highest = 1",
    sourceLabel: "Cost and tuition fields",
    confidenceLabel: school.costConfidence || school.dataConfidence || "Not available",
  };
}

function buildBaselineAttendance(school: ProductSchool): ComponentResult {
  if (school.attendanceScore === null) {
    return missingComponent(
      "baselineAttendance",
      "attendance",
      "Generated school context",
      "generated school context is unavailable, so it is excluded from the denominator.",
      "No applicant input",
      "Not available",
      "Generated attendance context score",
      "Generated payload attendance context",
      school.dataConfidence || "Not available",
    );
  }
  return {
    key: "baselineAttendance",
    group: "attendance",
    label: "Generated school context",
    value: clampScore(school.attendanceScore),
    detail: `Generated school context score is ${school.attendanceScore.toFixed(1)}`,
    warning: "",
    applicantValueLabel: "No applicant input",
    schoolValueLabel: school.attendanceScore.toFixed(1),
    formulaLabel: "Generated attendance context score",
    sourceLabel: "Generated payload attendance context",
    confidenceLabel: school.dataConfidence || "Not available",
  };
}

function missingComponent(
  key: LiveWeightKey,
  group: ComponentResult["group"],
  label: string,
  warning: string,
  applicantValueLabel: string,
  schoolValueLabel: string,
  formulaLabel: string,
  sourceLabel: string,
  confidenceLabel: string,
): ComponentResult {
  return {
    key,
    group,
    label,
    value: null,
    detail: "",
    warning,
    applicantValueLabel,
    schoolValueLabel,
    formulaLabel,
    sourceLabel,
    confidenceLabel,
  };
}

function buildContributionRow(component: ComponentResult, weights: LiveWeights, presentWeightSum: number): LiveContributionRow {
  const weight = weights[component.key];
  const included = weight > 0 && component.value !== null;
  const weightedPoints = included && presentWeightSum ? Math.round(((component.value * weight) / presentWeightSum) * 10) / 10 : null;
  const notIncludedReasonType: LiveNotIncludedReasonType | null = included ? null : weight === 0 ? "zero_weight" : "missing_data";
  const reason = included
    ? component.detail
    : weight === 0
      ? "Not included: weight is 0"
      : component.warning.replace(/\s+/g, " ").trim();

  return {
    componentKey: component.key,
    componentLabel: component.label,
    componentGroup: component.group,
    applicantValueLabel: component.applicantValueLabel,
    schoolValueLabel: component.schoolValueLabel,
    formulaLabel: component.formulaLabel,
    scoreValue: component.value,
    weight,
    presentWeightSum,
    weightedPoints,
    included,
    notIncludedReasonType,
    reason,
    sourceLabel: component.sourceLabel,
    confidenceLabel: component.confidenceLabel,
  };
}

function weightedAverage(contributions: LiveContribution[], weights: LiveWeights): number | null {
  const denominator = contributions.reduce((total, contribution) => total + weights[contribution.key], 0);
  if (!denominator) return null;
  const score = contributions.reduce((total, contribution) => total + contribution.value * weights[contribution.key], 0) / denominator;
  return Math.round(score * 10) / 10;
}

function buildCoverage(available: number, possible: number): LiveCoverage {
  const percent = possible ? Math.round((available / possible) * 100) : 0;
  const label: CoverageLabel = percent === 100 ? "full" : percent >= 60 ? "partial" : percent > 0 ? "limited" : "none";
  return { available, possible, percent, label };
}

function compareLiveScores(a: LiveSchoolScore, b: LiveSchoolScore, hasLiveScores: boolean): number {
  if (hasLiveScores) {
    if (a.yourScore !== null && b.yourScore === null) return -1;
    if (a.yourScore === null && b.yourScore !== null) return 1;
    if (a.yourScore !== null && b.yourScore !== null && a.yourScore !== b.yourScore) return b.yourScore - a.yourScore;
  }
  const aRank = a.baselineRank ?? 9999;
  const bRank = b.baselineRank ?? 9999;
  if (aRank !== bRank) return aRank - bRank;
  return a.school.name.localeCompare(b.school.name);
}

function compareAdjustedRows(a: SchoolAdjustedScore, b: SchoolAdjustedScore): number {
  const aScore = scoreValueForAdjustedRank(a);
  const bScore = scoreValueForAdjustedRank(b);
  if (aScore !== null && bScore === null) return -1;
  if (aScore === null && bScore !== null) return 1;
  if (aScore !== null && bScore !== null && aScore !== bScore) return bScore - aScore;
  const aRank = a.globalScore.baselineRank ?? 9999;
  const bRank = b.globalScore.baselineRank ?? 9999;
  if (aRank !== bRank) return aRank - bRank;
  return a.globalScore.school.name.localeCompare(b.globalScore.school.name);
}

function scoreValueForAdjustedRank(row: SchoolAdjustedScore): number | null {
  return row.adjustedScore?.yourScore ?? row.globalScore.yourScore;
}

type CostRange = {
  min: number | null;
  max: number | null;
};

function buildCostRange(schools: ProductSchool[], homeState: string): CostRange {
  const costs = schools.map((school) => applicableCost(school, homeState).value).filter((value): value is number => value !== null);
  if (!costs.length) return { min: null, max: null };
  return {
    min: Math.min(...costs),
    max: Math.max(...costs),
  };
}

type ApplicableCost = {
  value: number | null;
  detail: string;
};

function applicableCost(school: ProductSchool, homeState: string): ApplicableCost {
  const inState = firstPositiveCost(school.costInState, school.tuitionInState);
  const outState = firstPositiveCost(school.costOutState, school.tuitionOutState);
  const stateMatches = Boolean(homeState && school.stateAbbrev === homeState);

  if (stateMatches && inState !== null) {
    return { value: inState, detail: `Using in-state or single listed cost for selected home state ${homeState}.` };
  }
  if (stateMatches && outState !== null) {
    return { value: outState, detail: `In-state cost is unavailable; using the other positive listed cost as a single listed cost fallback.` };
  }
  if (homeState && outState !== null) {
    return { value: outState, detail: `Using out-of-state or single listed cost for selected home state ${homeState}.` };
  }
  if (homeState && inState !== null) {
    return { value: inState, detail: `Out-of-state cost is unavailable; using the other positive listed cost as a single listed cost fallback.` };
  }
  if (outState !== null) {
    return { value: outState, detail: "No home state selected; using out-of-state or single listed cost." };
  }
  if (inState !== null) {
    return { value: inState, detail: "No home state selected; using the available positive listed cost." };
  }
  return { value: null, detail: "" };
}

function firstPositiveCost(...values: unknown[]): number | null {
  for (const value of values) {
    const number = toPositiveNumberOrNull(value);
    if (number !== null) return number;
  }
  return null;
}

function effectFor(value: number): ContributionEffect {
  if (value >= 7.5) return "helps";
  if (value <= 4.5) return "hurts";
  return "neutral";
}

function clampScore(value: number): number {
  if (!Number.isFinite(value)) return 1;
  return Math.min(10, Math.max(1, value));
}

function formatDollars(value: number): string {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(value);
}
