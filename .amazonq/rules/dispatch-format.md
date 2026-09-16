# Dispatch Article Format — Canonical Spec

Every article in `src/content/dispatch/` must conform to this spec. It is the single
source of truth for frontmatter, structure, and the **Dispatch → Subject** motif.
If a piece deviates, fix the piece — never the spec.

---

## 1. The motif

Every Dispatch is introduced by the same kicker line:

```
DISPATCH → GLOBAL FINANCE
```

- `DISPATCH` is the fixed masthead word (electric cyan `#00D4FF`).
- The arrow `→` is the only separator between section and beat.
- **Subject** is the article's beat, rendered in uppercase from the `subject` field.

The motif appears in three places and must read identically in all of them:

| Location | Element |
|---|---|
| Article masthead | `The Dispatch → <Subject>` |
| Article header | `Dispatch → <Subject>` stamp above the headline |
| Dispatch index card | `Dispatch → <Subject>` stamp above the headline |

Never use roman numerals, "Part I", bold-wrapped headings, or italic headings.

---

## 2. Filename

- Lowercase **kebab-case**: `the-federal-reserve-and-the-dollar.md`
- No dates, no underscores, no uppercase, no special characters beyond hyphens.

## 3. Frontmatter

```yaml
---
title: "Who Makes Money When Missiles Fly"
subtitle: "A ledger of the firms that profit from the Iran war"
description: "Since February 2026, defense contractors have added billions in market cap while the cost is borne by civilians."
pubDate: 2026-06-18
category: investigation
subject: global-finance
tags:
  - iran-war
  - defense-contractors
  - military-industrial-complex
featured: true
---
```

Keys appear in exactly this order. Rules:

- **title** — Title Case, under 80 characters, no trailing period. Always double-quoted.
- **subtitle** *(optional)* — one short line that sharpens the headline (the old
  "deck"). Double-quoted. Omit the key entirely when unused.
- **description** — 1–2 plain-text sentences, no Markdown, no trailing ellipsis.
  Used for listings, SEO, and social cards. Always double-quoted.
- **pubDate** — ISO date only: `YYYY-MM-DD`. No time, no timezone, no quotes.
- **category** — the *genre* of the piece. One of:
  - `essay` — argument-driven or first-person analytical prose
  - `analysis` — evidence-based interpretation of events or ideas
  - `investigation` — sourced deep-dive exposing systems or hidden structures
  - `briefing` — concise factual update or explainer
- **subject** — the *beat*. One of:
  - `domestic-politics`
  - `world-affairs`
  - `global-finance`
  - `technology`
  - `surveillance-state`
  - `history`
  - `media-culture`
  - `science-health`
- **tags** — YAML block list only. Lowercase kebab-case, one per line, no quotes,
  no spaces, de-duplicated. Never an inline array.
- **featured** — unquoted boolean. `false` unless explicitly promoting the piece.

### Deprecated — do not use

- `category: dispatch`, `category: politics` (these were placeholders).
- Inline arrays: `tags: ["one", "two"]`.
- Timezone-aware dates: `2025-06-14T14:00:00Z`.
- Blank lines between frontmatter keys.

## 4. Body structure

1. **Never repeat the title, subtitle, category, date, or byline in the body.** The
   layout renders all of them from frontmatter as `<h1>` / header block.
2. Begin directly with body copy: an opening paragraph, or `## Section`.
3. Use `##` for major sections and `###` for subsections. Never skip a level.
   Never start a heading with `I.`, `1.`, or wrap it in `**`.
4. Keep headings in sentence case (`The dollar recycling engine`), not ALL-CAPS.
5. Paragraphs 3–5 sentences. Use `**bold**` for the first mention of a key proper
   noun or term; use italics only for emphasis, titles, and quoted words.
6. Separators between sections are a bare `---` on its own line (one blank line
   either side). Do not stack two rules together.
7. Use blockquotes only for direct quotations, and tables only for tabular data.

## 5. Sources block

A Dispatch that draws on external reporting ends with a sources section in
exactly this shape:

```md
---

## Sources

*The Guardian, BBC News, Amnesty International (2025), United Nations Human
Rights Council, company filings, witness testimony, declassified documents.*
```

- A bare `---` rule, a blank line, then the literal heading `## Sources`.
- One italic paragraph listing publications/institutions, separated by commas.
- For annotated bibliographies (title-by-title citations), use a bulleted list
  under the same `## Sources` heading instead of the paragraph.
- Never use `## Sources & Reading`, `### Sources`, or `**Sources:**` variants.
- A one-line provenance note may follow as a second italic paragraph.

## 6. Dates and ordering

`pubDate` is the article's real publication date, and it is the **only** thing that
decides where the piece appears — every Dispatch listing is ordered strictly
newest → oldest, across all subjects, with no grouping or per-beat sections.

### Where the date comes from

| Article | Date source |
|---|---|
| Published on the old WordPress site | `wp:post_date` — the *site-local* date WordPress displayed |
| Written after the migration (never on WordPress) | the day its file was first committed to this repository |

- **Never use `wp:post_date_gmt`.** The original migration did, which shifted
  every evening post forward a day and produced off-by-one dates.
- An article written after the migration may not be dated before the commit that
  created it. If it is, correct it to that commit date.
- Fixing dates is scripted: `python3 scripts/fix-dispatch-dates.py --check`,
  then re-run without `--check` to apply. The WordPress export lives (gitignored)
  at `_imports/mistykmedia.WordPress.2026-06-03.xml`; the authoritative
  slug → local-date table is embedded in the script so it stays reproducible.

### Ordering

- Ordering is a single shared comparator, `sortByNewest` in `src/lib/dispatch.ts`.
  Import it — never hand-roll a sort in a page, or the listings will drift apart.
- Ties on the same day are broken by title, then id, so the order is deterministic
  and stable across builds.

## 7. Voice

- Clear, direct, evidence-based. Let the facts carry the weight.
- Distinguish allegation, finding, and proven claim. Attribute contested claims.
- No sensationalism and no speculation presented as fact.

## 8. Pre-commit checklist

- [ ] Filename is kebab-case with no dates.
- [ ] Frontmatter keys in canonical order; `category` and `subject` both set from
      the allowed vocabularies.
- [ ] `pubDate` is `YYYY-MM-DD`, unquoted.
- [ ] `title`/`description` double-quoted; `tags` a block list, kebab-case, de-duped.
- [ ] Body opens with copy — no duplicate title, subtitle, or byline.
- [ ] Headings are clean `##` / `###`, no numerals, no bold, no italics.
- [ ] Ends with `---` + `## Sources`.
- [ ] `npm run build` passes.
