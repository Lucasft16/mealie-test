import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";
import { effectScope, ref } from "vue";
import { MEALPLAN_SCALE_SAVE_DELAY_MS, useMealPlanScale } from "../use-mealplan-scale";
import type { ReadPlanEntry } from "~/lib/api/types/meal-plan";

function createMeal(overrides: Partial<ReadPlanEntry> = {}): ReadPlanEntry {
  return {
    id: 1,
    date: "2026-08-19",
    entryType: "dinner",
    groupId: "my-group-id",
    userId: "my-user-id",
    householdId: "my-household-id",
    recipeId: "my-recipe-id",
    recipeScale: 1,
    recipe: { id: "my-recipe-id", name: "Pancakes", recipeServings: 4 },
    ...overrides,
  };
}

describe("useMealPlanScale", () => {
  const save = vi.fn();

  beforeEach(() => {
    vi.useFakeTimers();
    save.mockClear();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  test("starts at the scale of the entry", () => {
    const { scale } = useMealPlanScale(createMeal({ recipeScale: 2.5 }), save);
    expect(scale.value).toBe(2.5);
  });

  test("treats an entry without a scale as unscaled", () => {
    const { scale } = useMealPlanScale(createMeal({ recipeScale: undefined }), save);
    expect(scale.value).toBe(1);
  });

  test.each([0, -1, Number.NaN, Number.POSITIVE_INFINITY, Number.NEGATIVE_INFINITY])(
    "C12: starts at scale 1 when the entry contains %s",
    (invalidScale) => {
      const { scale } = useMealPlanScale(createMeal({ recipeScale: invalidScale }), save);

      expect(scale.value).toBe(1);
      vi.runAllTimers();
      expect(save).not.toHaveBeenCalled();
    },
  );

  test.each([0, -1, Number.NaN, Number.POSITIVE_INFINITY, Number.NEGATIVE_INFINITY])(
    "C12: normalizes refreshed scale %s without saving it back",
    (invalidScale) => {
      const meal = ref(createMeal({ recipeScale: 2 }));
      const { scale } = useMealPlanScale(meal, save);

      meal.value = createMeal({ recipeScale: invalidScale });

      expect(scale.value).toBe(1);
      vi.runAllTimers();
      expect(save).not.toHaveBeenCalled();
    },
  );

  test("C12: preserves a valid pending edit when refreshed with an invalid scale", () => {
    const meal = ref(createMeal({ recipeScale: 3 }));
    const { scale } = useMealPlanScale(meal, save);

    scale.value = 0.5;
    meal.value = createMeal({ recipeScale: Number.NaN });

    expect(scale.value).toBe(0.5);
    vi.advanceTimersByTime(MEALPLAN_SCALE_SAVE_DELAY_MS);
    expect(save).toHaveBeenCalledExactlyOnceWith({ ...meal.value, recipeScale: 0.5 });
  });

  test.each([
    [{ recipeServings: 4, recipeYieldQuantity: 12 }, 4],
    [{ recipeServings: 0, recipeYieldQuantity: 12 }, 12],
    [{ recipeServings: 0, recipeYieldQuantity: 0 }, 1],
    [{}, 1],
  ])("reads the servings of recipe %o as %d", (recipe, expected) => {
    const { recipeServings } = useMealPlanScale(createMeal({ recipe }), save);
    expect(recipeServings.value).toBe(expected);
  });

  test("saves a changed scale once the delay has passed", () => {
    const meal = createMeal();
    const { scale } = useMealPlanScale(meal, save);

    scale.value = 2;
    vi.advanceTimersByTime(MEALPLAN_SCALE_SAVE_DELAY_MS - 1);
    expect(save).not.toHaveBeenCalled();

    vi.advanceTimersByTime(1);
    expect(save).toHaveBeenCalledExactlyOnceWith({ ...meal, recipeScale: 2 });
  });

  test.each([0, -1, Number.NaN, Number.POSITIVE_INFINITY, Number.NEGATIVE_INFINITY])(
    "C11: does not save invalid scale %s after the delay",
    (invalidScale) => {
      const { scale } = useMealPlanScale(createMeal(), save);

      scale.value = invalidScale;
      vi.advanceTimersByTime(MEALPLAN_SCALE_SAVE_DELAY_MS);

      expect(save).not.toHaveBeenCalled();
    },
  );

  test.each(["flush", "dispose"])("C11: does not save an invalid edit on %s", (action) => {
    const scope = effectScope();
    const { scale, flush } = scope.run(() => useMealPlanScale(createMeal(), save))!;

    scale.value = 2;
    scale.value = 0;
    if (action === "flush") flush();
    scope.stop();
    vi.runAllTimers();

    expect(save).not.toHaveBeenCalled();
  });

  test("C11: saves a valid fractional scale after an invalid edit", () => {
    const meal = createMeal();
    const { scale } = useMealPlanScale(meal, save);

    scale.value = -1;
    vi.advanceTimersByTime(MEALPLAN_SCALE_SAVE_DELAY_MS);
    expect(save).not.toHaveBeenCalled();

    scale.value = 0.5;
    vi.advanceTimersByTime(MEALPLAN_SCALE_SAVE_DELAY_MS);
    expect(save).toHaveBeenCalledExactlyOnceWith({ ...meal, recipeScale: 0.5 });
  });

  test("saves only the last of several quick changes", () => {
    const { scale } = useMealPlanScale(createMeal(), save);

    scale.value = 1.25;
    vi.advanceTimersByTime(MEALPLAN_SCALE_SAVE_DELAY_MS - 1);
    scale.value = 1.5;
    vi.advanceTimersByTime(MEALPLAN_SCALE_SAVE_DELAY_MS - 1);
    scale.value = 1.75;
    expect(save).not.toHaveBeenCalled();

    vi.advanceTimersByTime(MEALPLAN_SCALE_SAVE_DELAY_MS);
    expect(save).toHaveBeenCalledOnce();
    expect(save).toHaveBeenCalledWith(expect.objectContaining({ recipeScale: 1.75 }));
  });

  test("doesn't save when the scale ends up where it started", () => {
    const { scale } = useMealPlanScale(createMeal({ recipeScale: 2 }), save);

    scale.value = 3;
    scale.value = 2;
    vi.runAllTimers();

    expect(save).not.toHaveBeenCalled();
  });

  test("follows the entry when it changes elsewhere, without saving it back", () => {
    const meal = ref(createMeal());
    const { scale } = useMealPlanScale(meal, save);

    meal.value = createMeal({ recipeScale: 3 });
    expect(scale.value).toBe(3);

    vi.runAllTimers();
    expect(save).not.toHaveBeenCalled();
  });

  test("keeps an unsaved edit when the entry is refreshed in the meantime", () => {
    const meal = ref(createMeal());
    const { scale } = useMealPlanScale(meal, save);

    scale.value = 2;
    meal.value = createMeal({ text: "refreshed" });
    meal.value = createMeal({ recipeScale: 1.5 });
    expect(scale.value).toBe(2);

    vi.runAllTimers();
    expect(save).toHaveBeenCalledOnce();
    expect(save).toHaveBeenCalledWith(expect.objectContaining({ recipeScale: 2 }));
  });

  test("uses the latest entry for the saved payload", () => {
    const meal = ref(createMeal());
    const { scale } = useMealPlanScale(meal, save);

    scale.value = 2;
    meal.value = createMeal({ entryType: "lunch" });
    vi.runAllTimers();

    expect(save).toHaveBeenCalledExactlyOnceWith(expect.objectContaining({ entryType: "lunch", recipeScale: 2 }));
  });

  test("saves a pending change right away when its scope is disposed", () => {
    const scope = effectScope();
    const { scale } = scope.run(() => useMealPlanScale(createMeal(), save))!;

    scale.value = 2;
    scope.stop();
    expect(save).toHaveBeenCalledOnce();

    vi.runAllTimers();
    expect(save).toHaveBeenCalledOnce();
  });

  test("has nothing to save on dispose when nothing changed", () => {
    const scope = effectScope();
    scope.run(() => useMealPlanScale(createMeal(), save));

    scope.stop();
    vi.runAllTimers();

    expect(save).not.toHaveBeenCalled();
  });
});
