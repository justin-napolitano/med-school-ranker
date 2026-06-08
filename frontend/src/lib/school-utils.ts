import { withBase } from "./site-url";

export type RawSchoolNode = Record<string, any>;

export type OwnershipFilter = "all" | "public" | "private" | "unknown";

export type LiveWeightKey = "mcatFit" | "gpaFit" | "stateFit" | "costFit" | "baselineAttendance";

export type LiveWeights = Record<LiveWeightKey, number>;

export type PreferenceState = {
  mcat: string;
  gpa: string;
  homeState: string;
  degree: "all" | "MD" | "DO";
  region: string;
  cost: "any" | "has-cost" | "lower-cost";
  excludedStates: string[];
  excludedCities: string[];
  ownershipType: OwnershipFilter;
  query: string;
  fit: "all" | "within" | "near" | "below" | "above" | "needs-inputs";
  liveWeights: LiveWeights;
};

export type ProductSchool = {
  id: string;
  slug: string;
  name: string;
  city: string;
  state: string;
  stateAbbrev: string;
  degree: string;
  profilePath: string;
  decisionRank: number | null;
  overallRank: number | null;
  rankLabel: string;
  rankBand: string;
  rankConfidence: string;
  rankScore: string;
  baselineScore: number | null;
  admissionsScore: number | null;
  attendanceScore: number | null;
  oosFriendlinessScore: number | null;
  rankSummary: string;
  schoolMcat: string;
  schoolGpa: string;
  publishedMcatBand: string;
  publishedGpaBand: string;
  statsQuality: string;
  statsSource: string;
  statsSourceUrl: string;
  statsSourceConfidence: string;
  statsSourceType: string;
  statsCohortYear: string;
  statsMetricPopulation: string;
  statsMetricType: string;
  websiteUrl: string;
  sourceName: string;
  sourceUrl: string;
  dataConfidence: string;
  costInState: string;
  costOutState: string;
  tuitionInState: string;
  tuitionOutState: string;
  costConfidence: string;
  ownershipType: "" | "public" | "private" | "unknown";
  policyCount: number;
  letterCount: number;
  positiveDrivers: string;
  negativeDrivers: string;
  missingDrivers: string;
  scoreWarnings: string;
  applicationBucket: string;
  aamcRateBand: string;
};

export type ProductPayload = {
  copy: Record<string, any>;
  meta: Record<string, any>;
  schools: ProductSchool[];
  methodology: Array<Record<string, any>>;
  curatedLists: Array<Record<string, any>>;
  sourceCount: number;
};

export const stateNames: Record<string, string> = {
  AL: "Alabama",
  AK: "Alaska",
  AZ: "Arizona",
  AR: "Arkansas",
  CA: "California",
  CO: "Colorado",
  CT: "Connecticut",
  DE: "Delaware",
  DC: "District of Columbia",
  FL: "Florida",
  GA: "Georgia",
  HI: "Hawaii",
  ID: "Idaho",
  IL: "Illinois",
  IN: "Indiana",
  IA: "Iowa",
  KS: "Kansas",
  KY: "Kentucky",
  LA: "Louisiana",
  ME: "Maine",
  MD: "Maryland",
  MA: "Massachusetts",
  MI: "Michigan",
  MN: "Minnesota",
  MS: "Mississippi",
  MO: "Missouri",
  MT: "Montana",
  NE: "Nebraska",
  NV: "Nevada",
  NH: "New Hampshire",
  NJ: "New Jersey",
  NM: "New Mexico",
  NY: "New York",
  NC: "North Carolina",
  ND: "North Dakota",
  OH: "Ohio",
  OK: "Oklahoma",
  OR: "Oregon",
  PA: "Pennsylvania",
  RI: "Rhode Island",
  SC: "South Carolina",
  SD: "South Dakota",
  TN: "Tennessee",
  TX: "Texas",
  UT: "Utah",
  VT: "Vermont",
  VA: "Virginia",
  WA: "Washington",
  WV: "West Virginia",
  WI: "Wisconsin",
  WY: "Wyoming",
};

const stateRegions: Record<string, string> = {
  CT: "Northeast",
  ME: "Northeast",
  MA: "Northeast",
  NH: "Northeast",
  RI: "Northeast",
  VT: "Northeast",
  NJ: "Northeast",
  NY: "Northeast",
  PA: "Northeast",
  IL: "Midwest",
  IN: "Midwest",
  MI: "Midwest",
  OH: "Midwest",
  WI: "Midwest",
  IA: "Midwest",
  KS: "Midwest",
  MN: "Midwest",
  MO: "Midwest",
  NE: "Midwest",
  ND: "Midwest",
  SD: "Midwest",
  DE: "South",
  FL: "South",
  GA: "South",
  MD: "South",
  NC: "South",
  SC: "South",
  VA: "South",
  DC: "South",
  WV: "South",
  AL: "South",
  KY: "South",
  MS: "South",
  TN: "South",
  AR: "South",
  LA: "South",
  OK: "South",
  TX: "South",
  AZ: "West",
  CO: "West",
  ID: "West",
  MT: "West",
  NV: "West",
  NM: "West",
  UT: "West",
  WY: "West",
  AK: "West",
  CA: "West",
  HI: "West",
  OR: "West",
  WA: "West",
};

export const defaultLiveWeights: LiveWeights = {
  mcatFit: 25,
  gpaFit: 25,
  stateFit: 20,
  costFit: 15,
  baselineAttendance: 15,
};

export const defaultPreferences: PreferenceState = {
  mcat: "",
  gpa: "",
  homeState: "FL",
  degree: "all",
  region: "all",
  cost: "any",
  excludedStates: [],
  excludedCities: [],
  ownershipType: "all",
  query: "",
  fit: "all",
  liveWeights: defaultLiveWeights,
};

export function normalizePayload(raw: any): ProductPayload {
  const schools = (raw.schools || []).map(normalizeSchool).sort(compareSchools);
  return {
    copy: raw.copy || {},
    meta: raw.meta || {},
    schools,
    methodology: raw.scoring_methodology || [],
    curatedLists: raw.curated_lists || [],
    sourceCount: raw.public_sources?.length || 0,
  };
}

export function normalizeSchool(node: RawSchoolNode): ProductSchool {
  const ranking = node.ranking || {};
  const school = node.school || {};
  const stats = node.admissions_stats || {};
  const cost = node.cost_and_debt || {};
  const derived = node.derived || {};
  const slug = ranking.school_slug || school.school_slug || node.school_slug || "";
  const costInState = firstPositiveValue(cost.estimated_coa_in_state, ranking.estimated_coa_in_state, school.estimated_coa_in_state);
  const costOutState = firstPositiveValue(cost.estimated_coa_out_state, ranking.estimated_coa_out_state, school.estimated_coa_out_state);
  const tuitionInState = firstPositiveValue(cost.in_state_tuition_fees_insurance, school.in_state_tuition_fees_insurance);
  const tuitionOutState = firstPositiveValue(cost.out_state_tuition_fees_insurance, school.out_state_tuition_fees_insurance);
  const statsSource = ranking.stats_source_name || stats.source_name || "";
  const statsSourceUrl = ranking.stats_source_url || stats.source_url || "";
  const statsSourceConfidence = ranking.stats_data_confidence || stats.data_confidence || "";
  return {
    id: ranking.school_id || school.school_id || slug,
    slug,
    name: ranking.school_name || school.school_name || stats.school_name || "Unknown school",
    city: ranking.city || school.city || "",
    state: ranking.state || school.state || "",
    stateAbbrev: ranking.state_abbrev || school.state_abbrev || "",
    degree: ranking.degree_type || school.degree_type || stats.degree_type || "",
    profilePath: withBase(`/schools/${slug}/`),
    decisionRank: toNumberOrNull(ranking.decision_rank),
    overallRank: toNumberOrNull(ranking.overall_rank),
    rankLabel: ranking.decision_rank_label || derived.application_bucket || "Unranked",
    rankBand: ranking.rank_band || derived.rank_band || "Incomplete data",
    rankConfidence: ranking.rank_confidence || derived.rank_confidence || "provisional",
    rankScore: ranking.overall_school_value || ranking.balanced_score || "",
    baselineScore: toNumberOrNull(ranking.overall_school_value || ranking.balanced_score),
    admissionsScore: toNumberOrNull(ranking.admissions_score || school.admissions_score),
    attendanceScore: toNumberOrNull(ranking.attendance_score || school.attendance_score),
    oosFriendlinessScore: toNumberOrNull(ranking.admissions_oos_friendliness_score || school.admissions_oos_friendliness_score),
    rankSummary: ranking.rank_summary || "",
    schoolMcat: ranking.school_mcat_for_fit || stats.published_mcat_average || school.median_mcat || "",
    schoolGpa: ranking.school_gpa_for_fit || stats.published_gpa_average || school.median_gpa || "",
    publishedMcatBand: ranking.published_mcat_band || stats.published_mcat_band || derived.published_mcat_band || "",
    publishedGpaBand: ranking.published_gpa_band || stats.published_gpa_band || derived.published_gpa_band || "",
    statsQuality: ranking.stats_data_quality_band || stats.data_quality_band || derived.admissions_data_quality_band || "",
    statsSource,
    statsSourceUrl,
    statsSourceConfidence,
    statsSourceType: statsSourceTypeFor(statsSourceConfidence, statsSource, statsSourceUrl),
    statsCohortYear: stats.stats_cohort_year || "",
    statsMetricPopulation: stats.metric_population || "",
    statsMetricType: stats.metric_type || "",
    websiteUrl: school.website || school.official_url || "",
    sourceName: ranking.source_name || school.source_name || "",
    sourceUrl: ranking.source_url || school.source_url || "",
    dataConfidence: ranking.data_confidence || statsSourceConfidence || school.data_confidence || "",
    costInState: costInState || costOutState,
    costOutState: costOutState || costInState,
    tuitionInState: tuitionInState || tuitionOutState,
    tuitionOutState: tuitionOutState || tuitionInState,
    costConfidence: cost.data_confidence || ranking.cost_data_confidence || "",
    ownershipType: normalizeOwnership(ranking.ownership_type || school.ownership_type),
    policyCount: Number(derived.admissions_policy_count || node.admissions_policies?.length || 0),
    letterCount: Number(derived.letter_requirement_count || node.letter_requirements?.length || 0),
    positiveDrivers: ranking.top_positive_drivers || ranking.top_positive_contributors || "",
    negativeDrivers: ranking.top_negative_drivers || ranking.top_negative_contributors || "",
    missingDrivers: ranking.missing_or_low_confidence_drivers || "",
    scoreWarnings: ranking.score_warnings || "",
    applicationBucket: ranking.application_bucket || derived.application_bucket || "",
    aamcRateBand: ranking.profile_aamc_acceptance_rate_band || stats.aamc_acceptance_rate_band || derived.aamc_acceptance_rate_band || "",
  };
}

export function compareSchools(a: ProductSchool, b: ProductSchool): number {
  const aRank = a.decisionRank ?? a.overallRank ?? 9999;
  const bRank = b.decisionRank ?? b.overallRank ?? 9999;
  if (aRank !== bRank) return aRank - bRank;
  return a.name.localeCompare(b.name);
}

export function filterSchools(schools: ProductSchool[], preferences: PreferenceState): ProductSchool[] {
  const query = preferences.query.trim().toLowerCase();
  const excludedStates = new Set(preferences.excludedStates);
  const excludedCities = new Set(preferences.excludedCities);
  const hasOwnershipLabels = schoolsHaveOwnershipLabels(schools);
  return schools
    .filter((school) => preferences.degree === "all" || school.degree === preferences.degree)
    .filter((school) => preferences.region === "all" || stateRegions[school.stateAbbrev] === preferences.region)
    .filter((school) => preferences.cost === "any" || hasCost(school))
    .filter((school) => !excludedStates.has(school.stateAbbrev))
    .filter((school) => !excludedCities.has(cityKeyForSchool(school)))
    .filter((school) => {
      if (!hasOwnershipLabels || preferences.ownershipType === "all") return true;
      return (school.ownershipType || "unknown") === preferences.ownershipType;
    })
    .filter((school) => {
      if (!query) return true;
      return [school.name, school.city, school.state, school.degree].join(" ").toLowerCase().includes(query);
    })
    .filter((school) => {
      if (preferences.fit === "all") return true;
      const fit = getScoreScreenFit(school, preferences).category;
      return fit === preferences.fit;
    })
    .sort((a, b) => {
      if (preferences.cost === "lower-cost") {
        const aCost = lowestListedCost(a) ?? 999999;
        const bCost = lowestListedCost(b) ?? 999999;
        if (aCost !== bCost) return aCost - bCost;
      }
      return compareSchools(a, b);
    });
}

export function getScoreScreenFit(school: ProductSchool, preferences: PreferenceState): { label: string; category: PreferenceState["fit"] } {
  const applicantMcat = toNumberOrNull(preferences.mcat);
  const applicantGpa = toNumberOrNull(preferences.gpa);
  if (applicantMcat === null || applicantGpa === null) {
    return { label: "Score-screen fit: needs MCAT/GPA inputs", category: "needs-inputs" };
  }

  const mcatRange = rangeFor(school.publishedMcatBand, school.schoolMcat, 2);
  const gpaRange = rangeFor(school.publishedGpaBand, school.schoolGpa, 0.08);
  if (!mcatRange && !gpaRange) {
    return { label: "Score-screen fit: needs published MCAT/GPA data", category: "needs-inputs" };
  }

  const mcatComparison = compareToRange(applicantMcat, mcatRange);
  const gpaComparison = compareToRange(applicantGpa, gpaRange);
  const comparisons = [mcatComparison, gpaComparison].filter(Boolean);

  if (comparisons.includes("below")) {
    return { label: "Score-screen fit: below published range", category: "below" };
  }
  if (comparisons.every((value) => value === "above")) {
    return { label: "Score-screen fit: above published range", category: "above" };
  }
  if (comparisons.every((value) => value === "within")) {
    return { label: "Score-screen fit: within published range", category: "within" };
  }
  return { label: "Score-screen fit: near published range", category: "near" };
}

export function buildWhyBullets(school: ProductSchool): string[] {
  const bullets: string[] = [];
  addBullet(bullets, school.rankSummary);
  for (const driver of splitDrivers(school.positiveDrivers).slice(0, 2)) {
    addBullet(bullets, `Positive driver: ${driver}.`);
  }
  for (const driver of splitDrivers(school.negativeDrivers).slice(0, 1)) {
    addBullet(bullets, `Review driver: ${driver}.`);
  }
  if (hasCost(school)) {
    addBullet(bullets, "Estimated cost data is available in the generated payload.");
  } else {
    addBullet(bullets, "Estimated cost data is not available in the generated payload.");
  }
  if (school.statsQuality) {
    addBullet(bullets, `MCAT/GPA source quality: ${school.statsQuality}.`);
  }
  const missing = missingSummary(school.missingDrivers || school.scoreWarnings);
  if (missing) {
    addBullet(bullets, `Missing or low-confidence context includes ${missing}.`);
  }
  return bullets.slice(0, 4);
}

export function formatCurrency(value: string): string {
  const number = toPositiveNumberOrNull(value);
  if (number === null) return "Not available";
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(number);
}

export function metricValue(value: string): string {
  return value?.trim() || "Not available";
}

export function hasCost(school: ProductSchool): boolean {
  return lowestListedCost(school) !== null;
}

export function statesForSchools(schools: ProductSchool[]): string[] {
  return Array.from(new Set(schools.map((school) => school.stateAbbrev).filter(Boolean))).sort();
}

export function stateLabel(state: string): string {
  return stateNames[state] ? `${state} - ${stateNames[state]}` : state;
}

export function cityKeyForSchool(school: ProductSchool): string {
  const city = school.city.trim();
  const state = (school.stateAbbrev || school.state).trim();
  return city && state ? `${city}|${state}` : "";
}

export function cityLabelFromKey(key: string): string {
  const [city, state] = key.split("|");
  return city && state ? `${city}, ${state}` : key;
}

export function cityOptionsForSchools(schools: ProductSchool[]): string[] {
  return Array.from(new Set(schools.map(cityKeyForSchool).filter(Boolean))).sort((a, b) => cityLabelFromKey(a).localeCompare(cityLabelFromKey(b)));
}

export function schoolsHaveOwnershipLabels(schools: ProductSchool[]): boolean {
  return schools.some((school) => school.ownershipType === "public" || school.ownershipType === "private");
}

export function ownershipLabel(value: OwnershipFilter): string {
  if (value === "public") return "Public";
  if (value === "private") return "Private";
  if (value === "unknown") return "Unknown";
  return "All ownership types";
}

export function toNumberOrNull(value: unknown): number | null {
  if (value === null || value === undefined || value === "") return null;
  const number = Number(String(value).replace(/[$,]/g, ""));
  return Number.isFinite(number) ? number : null;
}

export function toPositiveNumberOrNull(value: unknown): number | null {
  const number = toNumberOrNull(value);
  return number !== null && number > 0 ? number : null;
}

export function lowestListedCost(school: ProductSchool): number | null {
  const values = [school.costInState, school.costOutState, school.tuitionInState, school.tuitionOutState]
    .map(toPositiveNumberOrNull)
    .filter((value): value is number => value !== null);
  return values.length ? Math.min(...values) : null;
}

function firstPositiveValue(...values: unknown[]): string {
  for (const value of values) {
    if (toPositiveNumberOrNull(value) !== null) return String(value).trim();
  }
  return "";
}

function normalizeOwnership(value: unknown): ProductSchool["ownershipType"] {
  const normalized = String(value ?? "")
    .trim()
    .toLowerCase();
  if (!normalized) return "";
  if (normalized === "public" || normalized.includes("public")) return "public";
  if (normalized === "private" || normalized.includes("private")) return "private";
  return "unknown";
}

function statsSourceTypeFor(confidence: string, sourceName: string, sourceUrl: string): string {
  const text = [confidence, sourceName, sourceUrl].join(" ").toLowerCase();
  if (!text.trim()) return "missing";
  if (text.includes("official")) return "official public source";
  if (
    text.includes("third_party")
    || text.includes("third-party")
    || text.includes("shemmassian")
    || text.includes("prospectivedoctor")
    || text.includes("match guy")
  ) {
    return "provisional third-party source";
  }
  if (text.includes("cycletrack")) return "crowdsourced context";
  return "source-backed";
}

function addBullet(bullets: string[], value: string) {
  const clean = value?.replace(/\s+/g, " ").trim();
  if (clean) bullets.push(clean.endsWith(".") ? clean : `${clean}.`);
}

function splitDrivers(value: string): string[] {
  return value
    .split(/[;|]/)
    .map((part) => part.trim())
    .filter(Boolean);
}

function missingSummary(value: string): string {
  const cleaned = value.replace(/^missing:\s*/i, "").replace(/warnings?:/i, "warnings:");
  const parts = cleaned
    .split(/[;]/)
    .map((part) => part.trim())
    .filter(Boolean)
    .slice(0, 3);
  return parts.join(", ");
}

function rangeFor(band: string, fallbackAverage: string, fallbackSpread: number): [number, number] | null {
  const parsed = parseRange(band);
  if (parsed) return parsed;
  const average = toNumberOrNull(fallbackAverage);
  if (average === null) return null;
  return [average - fallbackSpread, average + fallbackSpread];
}

function parseRange(value: string): [number, number] | null {
  const clean = value?.trim();
  if (!clean) return null;
  const range = clean.match(/^([0-9.]+)\s*-\s*([0-9.]+)$/);
  if (range) return [Number(range[1]), Number(range[2])];
  const greater = clean.match(/^Greater than\s+([0-9.]+)$/i);
  if (greater) return [Number(greater[1]), Number.POSITIVE_INFINITY];
  const less = clean.match(/^Less than\s+([0-9.]+)$/i);
  if (less) return [Number.NEGATIVE_INFINITY, Number(less[1])];
  return null;
}

function compareToRange(value: number, range: [number, number] | null): "below" | "within" | "above" | null {
  if (!range) return null;
  const [min, max] = range;
  if (value < min) return "below";
  if (value > max) return "above";
  return "within";
}
