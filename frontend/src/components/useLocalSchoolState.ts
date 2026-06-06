import { useEffect, useMemo, useState } from "react";
import { defaultLiveWeights, defaultPreferences, type LiveWeights, type OwnershipFilter, type PreferenceState } from "../lib/school-utils";

const INTERESTED_KEY = "msr.product.interested.v1";
const APPLYING_KEY = "msr.product.applying.v1";
const NOT_INTERESTED_KEY = "msr.product.notInterested.v1";
const COMPARE_KEY = "msr.product.compare.v1";
const PREFERENCES_KEY = "msr.product.preferences.v1";

export const INTERESTED_MAX = 50;
export const APPLYING_MAX = 25;
export const COMPARE_MAX = 4;

function readArray(key: string): string[] {
  try {
    const value = window.localStorage.getItem(key);
    const parsed = value ? JSON.parse(value) : [];
    return Array.isArray(parsed) ? parsed.filter((item) => typeof item === "string") : [];
  } catch {
    return [];
  }
}

function readPreferences(): PreferenceState {
  try {
    const value = window.localStorage.getItem(PREFERENCES_KEY);
    return value ? normalizePreferences(JSON.parse(value)) : defaultPreferences;
  } catch {
    return defaultPreferences;
  }
}

function normalizePreferences(value: Partial<PreferenceState> | null): PreferenceState {
  const next = { ...defaultPreferences, ...(value || {}) };
  const liveWeights = typeof value?.liveWeights === "object" && value.liveWeights ? value.liveWeights : {};
  return {
    ...next,
    excludedStates: normalizeStringArray(value?.excludedStates),
    excludedCities: normalizeStringArray(value?.excludedCities),
    ownershipType: normalizeOwnershipFilter(value?.ownershipType),
    liveWeights: normalizeWeights(liveWeights),
  };
}

function normalizeStringArray(value: unknown): string[] {
  return Array.isArray(value) ? value.filter((item): item is string => typeof item === "string" && item.trim().length > 0) : [];
}

function normalizeOwnershipFilter(value: unknown): OwnershipFilter {
  return value === "public" || value === "private" || value === "unknown" || value === "all" ? value : "all";
}

function normalizeWeights(value: Partial<LiveWeights>): LiveWeights {
  return {
    mcatFit: normalizeWeight(value.mcatFit, defaultLiveWeights.mcatFit),
    gpaFit: normalizeWeight(value.gpaFit, defaultLiveWeights.gpaFit),
    stateFit: normalizeWeight(value.stateFit, defaultLiveWeights.stateFit),
    costFit: normalizeWeight(value.costFit, defaultLiveWeights.costFit),
    baselineAttendance: normalizeWeight(value.baselineAttendance, defaultLiveWeights.baselineAttendance),
  };
}

function normalizeWeight(value: unknown, fallback: number): number {
  const number = Number(value);
  return Number.isFinite(number) && number >= 0 ? number : fallback;
}

function unique(values: string[]): string[] {
  return Array.from(new Set(values));
}

export function useLocalSchoolState() {
  const [ready, setReady] = useState(false);
  const [interested, setInterested] = useState<string[]>([]);
  const [applying, setApplying] = useState<string[]>([]);
  const [notInterested, setNotInterested] = useState<string[]>([]);
  const [compare, setCompare] = useState<string[]>([]);
  const [preferences, setPreferencesState] = useState<PreferenceState>(defaultPreferences);
  const [notice, setNotice] = useState("");

  useEffect(() => {
    setInterested(readArray(INTERESTED_KEY).slice(0, INTERESTED_MAX));
    setApplying(readArray(APPLYING_KEY).slice(0, APPLYING_MAX));
    setNotInterested(readArray(NOT_INTERESTED_KEY));
    setCompare(readArray(COMPARE_KEY).slice(0, COMPARE_MAX));
    setPreferencesState(readPreferences());
    setReady(true);
  }, []);

  useEffect(() => {
    if (ready) window.localStorage.setItem(INTERESTED_KEY, JSON.stringify(interested));
  }, [interested, ready]);

  useEffect(() => {
    if (ready) window.localStorage.setItem(APPLYING_KEY, JSON.stringify(applying));
  }, [applying, ready]);

  useEffect(() => {
    if (ready) window.localStorage.setItem(NOT_INTERESTED_KEY, JSON.stringify(notInterested));
  }, [notInterested, ready]);

  useEffect(() => {
    if (ready) window.localStorage.setItem(COMPARE_KEY, JSON.stringify(compare));
  }, [compare, ready]);

  useEffect(() => {
    if (ready) window.localStorage.setItem(PREFERENCES_KEY, JSON.stringify(preferences));
  }, [preferences, ready]);

  function setPreferences(next: PreferenceState) {
    setPreferencesState(normalizePreferences(next));
  }

  function updatePreference<K extends keyof PreferenceState>(key: K, value: PreferenceState[K]) {
    setPreferencesState((current) => normalizePreferences({ ...current, [key]: value }));
  }

  function addInterested(slug: string) {
    setInterested((current) => {
      if (current.includes(slug)) return current;
      if (current.length >= INTERESTED_MAX) {
        setNotice(`Interested is capped at ${INTERESTED_MAX} schools.`);
        return current;
      }
      setNotice("");
      setNotInterested((hidden) => hidden.filter((item) => item !== slug));
      return unique([...current, slug]);
    });
  }

  function removeInterested(slug: string) {
    setInterested((current) => current.filter((item) => item !== slug));
  }

  function addApplying(slug: string) {
    setApplying((current) => {
      if (current.includes(slug)) return current;
      if (current.length >= APPLYING_MAX) {
        setNotice(`Applying is capped at ${APPLYING_MAX} schools.`);
        return current;
      }
      setNotice("");
      setNotInterested((hidden) => hidden.filter((item) => item !== slug));
      return unique([...current, slug]);
    });
  }

  function removeApplying(slug: string) {
    setApplying((current) => current.filter((item) => item !== slug));
  }

  function addNotInterested(slug: string) {
    setNotice("");
    setInterested((current) => current.filter((item) => item !== slug));
    setApplying((current) => current.filter((item) => item !== slug));
    setCompare((current) => current.filter((item) => item !== slug));
    setNotInterested((current) => (current.includes(slug) ? current : unique([...current, slug])));
  }

  function removeNotInterested(slug: string) {
    setNotInterested((current) => current.filter((item) => item !== slug));
  }

  function toggleCompare(slug: string) {
    setCompare((current) => {
      if (current.includes(slug)) return current.filter((item) => item !== slug);
      if (current.length >= COMPARE_MAX) {
        setNotice(`Compare is capped at ${COMPARE_MAX} schools.`);
        return current;
      }
      setNotice("");
      return unique([...current, slug]);
    });
  }

  function exportState(scope: "interested" | "applying" | "notInterested") {
    const payload = {
      exported_at: new Date().toISOString(),
      scope,
      slugs: scope === "interested" ? interested : scope === "applying" ? applying : notInterested,
      preferences,
    };
    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `${scope}-schools.json`;
    link.click();
    URL.revokeObjectURL(url);
  }

  return useMemo(
    () => ({
      ready,
      interested,
      applying,
      notInterested,
      compare,
      preferences,
      notice,
      setPreferences,
      updatePreference,
      addInterested,
      removeInterested,
      addApplying,
      removeApplying,
      addNotInterested,
      removeNotInterested,
      toggleCompare,
      exportState,
      isInterested: (slug: string) => interested.includes(slug),
      isApplying: (slug: string) => applying.includes(slug),
      isNotInterested: (slug: string) => notInterested.includes(slug),
      isCompared: (slug: string) => compare.includes(slug),
    }),
    [ready, interested, applying, notInterested, compare, preferences, notice],
  );
}

export type LocalSchoolState = ReturnType<typeof useLocalSchoolState>;
