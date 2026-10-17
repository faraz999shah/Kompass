import en from "../../i18n/locales/en.json";
import es from "../../i18n/locales/es.json";
import sw from "../../i18n/locales/sw.json";
import {
  ACCESSIBILITY_OPTIONS,
  COMFORT_OPTIONS,
  COUNTRIES,
  GOAL_OPTIONS,
  LIFE_STAGE_OPTIONS,
} from "../choices";

const LOCALES = { en, es, sw };
const ALL_CHOICES = [
  ...ACCESSIBILITY_OPTIONS,
  ...LIFE_STAGE_OPTIONS,
  ...GOAL_OPTIONS,
  ...COMFORT_OPTIONS,
];

function lookup(locale: object, key: string): unknown {
  return key
    .split(".")
    .reduce<unknown>(
      (node, part) =>
        node && typeof node === "object"
          ? (node as Record<string, unknown>)[part]
          : undefined,
      locale,
    );
}

describe("setup choices", () => {
  it.each(Object.entries(LOCALES))(
    "has a label and a spoken hint for every choice in %s",
    (_language, locale) => {
      for (const choice of ALL_CHOICES) {
        expect(lookup(locale, choice.labelKey)).toEqual(expect.any(String));
        expect(lookup(locale, choice.hintKey)).toEqual(expect.any(String));
      }
    },
  );

  it.each(Object.entries(LOCALES))(
    "names every country in %s",
    (_language, locale) => {
      for (const { countryCode } of COUNTRIES) {
        expect(lookup(locale, `onboarding.country.${countryCode}`)).toEqual(
          expect.any(String),
        );
      }
    },
  );

  it("offers Swahili only in Kenya and Spanish only in the Americas", () => {
    const languagesBy = Object.fromEntries(
      COUNTRIES.map((country) => [
        country.countryCode,
        country.supportedLanguages,
      ]),
    );

    expect(languagesBy).toEqual({
      US: ["en", "es"],
      MX: ["es", "en"],
      KE: ["en", "sw"],
    });
  });

  it("uses unique ids within each group", () => {
    for (const group of [
      ACCESSIBILITY_OPTIONS,
      LIFE_STAGE_OPTIONS,
      GOAL_OPTIONS,
      COMFORT_OPTIONS,
    ]) {
      const ids = group.map((choice) => choice.id);
      expect(new Set(ids).size).toBe(ids.length);
    }
  });
});
