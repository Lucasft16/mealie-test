/**
 * Truncates plain text to `length` characters, appending `clamp` when truncated.
 *
 * The input is treated strictly as text and is never parsed as HTML, so markup in the input is
 * returned verbatim rather than interpreted.
 */
export function truncateText(text: string, length = 20, clamp = "..."): string {
  const segmenter = new Intl.Segmenter(undefined, { granularity: "grapheme" });
  const chars = Array.from(segmenter.segment(text), (s) => s.segment);
  return chars.length > length ? chars.slice(0, length).join("") + clamp : text;
}
