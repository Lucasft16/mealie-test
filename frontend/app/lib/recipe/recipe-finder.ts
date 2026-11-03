export function normalizeMissingItemLimit(value: number | null | undefined): number {
  const limit = value ?? 0;
  if (!Number.isFinite(limit)) {
    return 0;
  }
  return Math.max(0, limit);
}
