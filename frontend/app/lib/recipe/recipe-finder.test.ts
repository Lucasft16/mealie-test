import { describe, expect, it } from "vitest";

import { normalizeMissingItemLimit } from "./recipe-finder";

describe("normalizeMissingItemLimit", () => {
  it("preserves non-negative limits", () => {
    expect(normalizeMissingItemLimit(0)).toBe(0);
    expect(normalizeMissingItemLimit(20)).toBe(20);
  });

  it("clamps negative limits to zero", () => {
    expect(normalizeMissingItemLimit(-1)).toBe(0);
  });

  it("normalizes an empty input to zero", () => {
    expect(normalizeMissingItemLimit(null)).toBe(0);
    expect(normalizeMissingItemLimit(undefined)).toBe(0);
  });
  it.each([NaN, Infinity])("normalizes %s to zero", (value) => {
    expect(normalizeMissingItemLimit(value)).toBe(0);
  });

  it("keeps -Infinity at zero (regression)", () => {
    expect(normalizeMissingItemLimit(-Infinity)).toBe(0);
  });
  it.each([
    [2.7, 2],
    [0.9, 0],
    [19.999, 19],
  ])("truncates fractional limit %s to %s", (value, expected) => {
    expect(normalizeMissingItemLimit(value)).toBe(expected);
  });

  it("keeps integer limits unchanged (regression)", () => {
    expect(normalizeMissingItemLimit(2)).toBe(2);
  });
});
