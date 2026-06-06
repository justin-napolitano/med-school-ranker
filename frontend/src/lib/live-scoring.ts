import type { LiveWeightKey, LiveWeights, PreferenceState, ProductSchool } from "./school-utils";
import { toNumberOrNull } from "./school-utils";

type ContributionEffect = "helps" | "hurts" | "neutral";
type CoverageLabel = "full" | "partial" | "limited" | "none";

export type LiveContribution = {
  key: LiveWeightKey;
  label: string;
  value: number;
  weight: number;
  effect: ContributionEffect;
  detail: string;
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
  liveWarnings: string[];
};

type ComponentResult = {
  key: LiveWeightKey;
  group: "admissions" | "attendance";
  label: string;
  value: number | null;
  detail: string;
  warning: string;
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
  baselineAttendance: "Uses generated attendance context from the existing payload.",
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
    liveWarnings,
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
    return missingComponent("mcatFit", "admissions", "MCAT fit", "applicant MCAT or school MCAT is unavailable, so MCAT is excluded from the denominator.");
  }
  return {
    key: "mcatFit",
    group: "admissions",
    label: "MCAT fit",
    value: clampScore(7 + (applicantMcat - schoolMcat) / 2),
    detail: `Applicant MCAT ${applicantMcat} compared with school MCAT ${schoolMcat}`,
    warning: "",
  };
}

function buildGpaFit(school: ProductSchool, preferences: PreferenceState): ComponentResult {
  const applicantGpa = toNumberOrNull(preferences.gpa);
  const schoolGpa = toNumberOrNull(school.schoolGpa);
  if (applicantGpa === null || schoolGpa === null) {
    return missingComponent("gpaFit", "admissions", "GPA fit", "applicant GPA or school GPA is unavailable, so GPA is excluded from the denominator.");
  }
  return {
    key: "gpaFit",
    group: "admissions",
    label: "GPA fit",
    value: clampScore(7 + (applicantGpa - schoolGpa) / 0.08),
    detail: `Applicant GPA ${applicantGpa.toFixed(2)} compared with school GPA ${schoolGpa.toFixed(2)}`,
    warning: "",
  };
}

function buildStateFit(school: ProductSchool, preferences: PreferenceState): ComponentResult {
  const homeState = preferences.homeState;
  if (!homeState) {
    return missingComponent("stateFit", "admissions", "State/residency fit", "home state is not selected, so state/residency fit is excluded from the denominator.");
  }
  if (school.stateAbbrev === homeState) {
    return {
      key: "stateFit",
      group: "admissions",
      label: "State/residency fit",
      value: 10,
      detail: `${school.stateAbbrev} matches selected home state ${homeState}`,
      warning: "",
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
    };
  }
  return missingComponent("stateFit", "admissions", "State/residency fit", "OOS context is unavailable for this school, so state/residency fit is excluded from the denominator.");
}

function buildCostFit(school: ProductSchool, preferences: PreferenceState, costRange: CostRange): ComponentResult {
  const cost = applicableCost(school, preferences.homeState);
  if (cost === null || costRange.min === null || costRange.max === null) {
    return missingComponent("costFit", "attendance", "Cost fit", "applicable cost data is unavailable, so cost is excluded from the denominator.");
  }
  const value = costRange.max === costRange.min ? 10 : 10 - ((cost - costRange.min) / (costRange.max - costRange.min)) * 9;
  return {
    key: "costFit",
    group: "attendance",
    label: "Cost fit",
    value: clampScore(value),
    detail: `Applicable listed cost is ${formatDollars(cost)}`,
    warning: "",
  };
}

function buildBaselineAttendance(school: ProductSchool): ComponentResult {
  if (school.attendanceScore === null) {
    return missingComponent(
      "baselineAttendance",
      "attendance",
      "Baseline attendance context",
      "generated attendance context is unavailable, so it is excluded from the denominator.",
    );
  }
  return {
    key: "baselineAttendance",
    group: "attendance",
    label: "Baseline attendance context",
    value: clampScore(school.attendanceScore),
    detail: `Generated attendance context score is ${school.attendanceScore.toFixed(1)}`,
    warning: "",
  };
}

function missingComponent(key: LiveWeightKey, group: ComponentResult["group"], label: string, warning: string): ComponentResult {
  return {
    key,
    group,
    label,
    value: null,
    detail: "",
    warning,
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

type CostRange = {
  min: number | null;
  max: number | null;
};

function buildCostRange(schools: ProductSchool[], homeState: string): CostRange {
  const costs = schools.map((school) => applicableCost(school, homeState)).filter((value): value is number => value !== null);
  if (!costs.length) return { min: null, max: null };
  return {
    min: Math.min(...costs),
    max: Math.max(...costs),
  };
}

function applicableCost(school: ProductSchool, homeState: string): number | null {
  const inState = toNumberOrNull(school.costInState);
  const outState = toNumberOrNull(school.costOutState);
  if (homeState && school.stateAbbrev === homeState) return inState ?? outState;
  if (homeState) return outState ?? inState;
  return outState ?? inState;
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
