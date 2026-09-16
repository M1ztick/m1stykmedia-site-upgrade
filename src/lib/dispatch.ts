/**
 * Dispatch motif — the single source of truth for the section's "kicker".
 *
 * Every Dispatch is introduced by the same line:
 *
 *     DISPATCH → GLOBAL FINANCE
 *
 * `Dispatch` is the fixed masthead word; the arrow is the only separator; the
 * subject is the article's beat, rendered from the `subject` frontmatter field.
 * Import these helpers anywhere the motif appears so the three placements
 * (masthead, article header, index card) can never drift apart.
 */

export const DISPATCH_PREFIX = 'Dispatch';

export const SUBJECTS = {
  'domestic-politics': 'Domestic Politics',
  'world-affairs': 'World Affairs',
  'global-finance': 'Global Finance',
  technology: 'Technology',
  'surveillance-state': 'Surveillance State',
  history: 'History',
  'media-culture': 'Media & Culture',
  'science-health': 'Science & Health',
} as const;

export type Subject = keyof typeof SUBJECTS;

export const SUBJECT_SLUGS = Object.keys(SUBJECTS) as Subject[];

/** Human-readable label for a subject slug, with a safe fallback. */
export function subjectLabel(subject?: string | null): string {
  if (subject && subject in SUBJECTS) return SUBJECTS[subject as Subject];
  return 'Dispatch';
}

/** Full motif string, e.g. `Dispatch → Global Finance`. */
export function motif(subject?: string | null): string {
  return `${DISPATCH_PREFIX} \u2192 ${subjectLabel(subject)}`;
}

/**
 * Shared ordering for every Dispatch listing: strictly newest → oldest.
 *
 * Articles are ordered by `pubDate` alone — never grouped or reordered by
 * subject — so the feed reads the same no matter what each piece is about.
 * Ties are broken by title (then id) so the order is deterministic and stable
 * across builds rather than depending on the collection's read order.
 */
export function byNewest<
  T extends { id: string; data: { pubDate: Date | string; title?: string } },
>(a: T, b: T): number {
  const delta =
    new Date(b.data.pubDate).getTime() - new Date(a.data.pubDate).getTime();
  if (delta !== 0) return delta;
  const byTitle = (a.data.title ?? '').localeCompare(b.data.title ?? '');
  return byTitle !== 0 ? byTitle : a.id.localeCompare(b.id);
}

/** Convenience wrapper: returns a new newest-first array (does not mutate). */
export function sortByNewest<
  T extends { id: string; data: { pubDate: Date | string; title?: string } },
>(entries: T[]): T[] {
  return [...entries].sort(byNewest);
}
