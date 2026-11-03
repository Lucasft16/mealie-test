// Segmentador de grafemas (trata emojis simples e letras com acentos combinantes como 1 caractere visual)
const GRAPHEME_SEGMENTER = new Intl.Segmenter(undefined, { granularity: "grapheme" });

/**
 * Truncates plain text to `length` characters, appending `clamp` when truncated.
 *
 * The input is treated strictly as text and is never parsed as HTML, so markup in the input is
 * returned verbatim rather than interpreted.
 */
export function truncateText(text: string, length = 20, clamp = "..."): string {
  const chars = Array.from(GRAPHEME_SEGMENTER.segment(text), (s) => s.segment);
  return chars.length > length ? chars.slice(0, length).join("") + clamp : text;
}
