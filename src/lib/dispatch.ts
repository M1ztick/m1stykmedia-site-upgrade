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
