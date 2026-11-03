export function normalizeMissingItemLimit(value: number | null | undefined): number {
  const limit = value ?? 0;
  return Number.isFinite(limit) ? Math.max(0, limit) : 0;
}
