# Dispatch Article Format Rules

These rules govern every article in `src/content/dispatch/` for the MistykMedia site.

## File naming convention

- Use lowercase kebab-case: `article-title-keywords.md`
- No dates in filenames
- No special characters except hyphens

## Required frontmatter fields

```yaml
---
title: "Article Title in Title Case"
description: "A compelling 1-2 sentence summary of the article."
pubDate: 2026-06-18
category: investigation
subject: tech-surveillance
tags:
  - palantir
  - surveillance
  - civil-liberties
featured: false
---
```

### Field definitions

- **title**: Title case or sentence case; keep under 80 characters; no trailing period.
- **description**: 1–2 sentences; plain text; no Markdown; shown in listings and SEO.
- **pubDate**: ISO date only: `YYYY-MM-DD`. No time, no timezone, no quotes.
- **category**: The genre/format of the piece. Must be one of:
  - `essay` — argument-driven first-person or analytical prose
  - `analysis` — evidence-based interpretation of events or ideas
  - `investigation` — reported or sourced deep-dive exposing systems, patterns, or hidden structures
  - `briefing` — concise factual update or explainer
- **subject**: The beat or topic area of the piece. Must be one of:
  - `world-affairs`
  - `domestic-politics`
  - `global-finance`
  - `economics`
  - `tech-surveillance`
  - `history`
  - `culture`
  - `media`
  - `labor`
  - `climate`
  - `health`
- **tags**: Block-list format only (kebab-case, lowercase, no spaces). Convert spaces to hyphens, remove quotes, remove special characters.
- **featured**: Boolean. Use `false` unless explicitly promoting the piece.

### Deprecated

- `category: dispatch` — this was a placeholder. Replace with both `category` and `subject`.
- Inline tag arrays such as `tags: ["tag one", "tag two"]` — always use block-list syntax.
- Timezone-aware pubDates such as `2025-06-14T14:00:00Z` — use date only.

## Body structure

1. Do **not** repeat the title/heading at the top of the body. The layout renders the frontmatter title as `<h1>`.
2. Begin with `## I. First Section` or `## First Section`. Be consistent within a single article.
3. Use `##` for major sections and `###` for subsections.
4. Use bold for the first mention of key proper nouns, institutions, or technical terms within a section.
5. Keep paragraphs relatively short (3–5 sentences) for readability.
6. Use blockquotes only for direct quotations.
7. End every article with a standardized sources block.

## Sources block

Use exactly this format at the end of the article:

```md
---

*Sources: The Guardian, BBC News, Amnesty International (2025), United Nations Human Rights Council, company filings, witness testimony, declassified documents.*
```

- Begin with a horizontal rule `---`.
- Follow with an italic paragraph beginning `*Sources:` and ending with `*`.
- Do not use a `## Sources` or `## Sources & Reading` header.
- List publications and institutions, optionally including year or document type.
- If sources are numerous or sensitive, summarize rather than enumerating every citation.

## Style and tone

- Clear, direct, and evidence-based.
- Avoid sensationalism; let the facts carry weight.
- Distinguish between allegations, findings, and proven claims.
- Attribute contested claims to specific reports, institutions, or reporters.
- Avoid speculative claims presented as fact.

## Internal consistency

Dispatch articles should feel like a coherent series. Maintain consistent:
- heading style,
- date format,
- tag conventions,
- sources block format,
- framing of uncertain or contested claims.
