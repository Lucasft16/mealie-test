import type { ReadPlanEntry, UpdatePlanEntry } from "~/lib/api/types/meal-plan";

export const MEALPLAN_SCALE_SAVE_DELAY_MS = 400;

function isValidScale(value: number): boolean {
  return Number.isFinite(value) && value > 0;
}

/**
 * Keeps the recipe scale while the user edits it.
 * Saves the last value after no changes for `delay` ms.
 */
export function useMealPlanScale(
  meal: MaybeRefOrGetter<ReadPlanEntry>,
  save: (payload: UpdatePlanEntry) => unknown,
  delay = MEALPLAN_SCALE_SAVE_DELAY_MS,
) {
  const savedScale = computed(() => {
    const value = toValue(meal).recipeScale ?? 1;
    return isValidScale(value) ? value : 1;
  });
  const scale = ref(savedScale.value);

  // Use 1 if the recipe has no serving count or yield quantity.
  const recipeServings = computed(() => {
    const recipe = toValue(meal).recipe;
    return recipe?.recipeServings || recipe?.recipeYieldQuantity || 1;
  });

  let saveTimer: ReturnType<typeof setTimeout> | null = null;

  function saveNow() {
    saveTimer = null;
    if (isValidScale(scale.value) && scale.value !== savedScale.value) {
      save({ ...toValue(meal), recipeScale: scale.value });
    }
  }

  /** Saves the change now, without waiting. */
  function flush() {
    if (saveTimer) {
      clearTimeout(saveTimer);
      saveNow();
    }
  }

  watch(scale, () => {
    if (saveTimer) {
      clearTimeout(saveTimer);
      saveTimer = null;
    }
    if (scale.value !== savedScale.value) {
      saveTimer = setTimeout(saveNow, delay);
    }
  }, { flush: "sync" });

  watch(savedScale, (newScale) => {
    // Keep the user's edit if it is still waiting to be saved.
    if (!saveTimer) {
      scale.value = newScale;
    }
  }, { flush: "sync" });

  // Save any waiting change when the user leaves the control.
  if (getCurrentScope()) {
    onScopeDispose(flush);
  }

  return {
    scale,
    recipeServings,
    flush,
  };
}
