import type {
  Country,
  Goal,
  Language,
  LifeStage,
  Topic,
} from "@/src/types/api";

// The choices the setup screens offer. Screens render these lists rather than
// hard-coding ids; the words live in src/i18n/locales under "onboarding".

/** One choice on a setup screen, with the i18n keys for its label and spoken hint. */
export type SetupChoice<Id extends string> = {
  id: Id;
  labelKey: string;
  hintKey: string;
};

/** The setup screens' accessibility toggles. */
export type AccessibilityToggle = "readAloud" | "simpleMode" | "largerText";

/** "Money feels…" answers, sent to the API as comfort 1 to 3. */
export type ComfortLevel = "beginner" | "somewhat_comfortable" | "confident";

/** Lesson topics in the order the confidence sliders ask about them. */
export const TOPICS: readonly Topic[] = [
  "accounts",
  "saving",
  "borrowing",
  "scams",
  "budget",
];

/** Countries in picker order; each lists its lesson languages, default first. */
export const COUNTRIES: readonly {
  countryCode: Country;
  supportedLanguages: readonly Language[];
}[] = [
  { countryCode: "US", supportedLanguages: ["en", "es"] },
  { countryCode: "MX", supportedLanguages: ["es", "en"] },
  { countryCode: "KE", supportedLanguages: ["en", "sw"] },
];

function choicesFor<Id extends string>(
  group: string,
  ids: readonly Id[],
): SetupChoice<Id>[] {
  return ids.map((id) => ({
    id,
    labelKey: `onboarding.${group}.${id}.label`,
    hintKey: `onboarding.${group}.${id}.hint`,
  }));
}

export const ACCESSIBILITY_OPTIONS = choicesFor<AccessibilityToggle>(
  "accessibility",
  ["readAloud", "simpleMode", "largerText"],
);

export const LIFE_STAGE_OPTIONS = choicesFor<LifeStage>("lifeStage", [
  "student",
  "first_job",
  "parent",
  "retired",
]);

export const GOAL_OPTIONS = choicesFor<Goal>("goal", [
  "save_more",
  "avoid_debt",
  "stay_safe_online",
  "handle_emergencies",
]);

export const COMFORT_OPTIONS = choicesFor<ComfortLevel>("comfort", [
  "beginner",
  "somewhat_comfortable",
  "confident",
]);
