# Dispatch Article Format Spec

All articles in `src/content/dispatch/` must conform to this spec before being committed.

---

## Frontmatter

```yaml
---
title: "Article Title Here"
description: "One or two sentence deck. No trailing ellipsis."
pubDate: YYYY-MM-DD
tags:
  - kebab-case-tag
  - another-tag
category: essay | politics | investigation
featured: true | false
---
```

Rules:
- No blank lines between frontmatter keys
- `title` and `description` always quoted
- `tags` always YAML block list (one tag per line, `- kebab-case`), never inline array
- `pubDate` is `YYYY-MM-DD` with no quotes
- `category` is one of: `essay`, `politics`, `investigation`
- `featured` is unquoted boolean

---

## Filename

- All lowercase, hyphen-separated: `the-article-title.md`
- No underscores, no uppercase

---

## Body Structure

### What NOT to include at the top of the body

The layout renders the title, description, category, date, and byline from frontmatter. Do **not** repeat any of these in the body:

```md
<!-- BAD — remove these -->
# DISPATCH
## Article Title
*A subtitle or deck line*
---
```

Start the body directly with the first section header or opening prose.

### Header hierarchy

- `##` for major sections (Roman numerals or descriptive titles)
- `###` for subsections
- No `#` (h1) in the body — the layout owns h1

### Section labels (plain text → headers)

Old WordPress-era articles used plain text as section labels (no `#`). These must be converted to `##` headers:

```md
<!-- BAD -->
The Origins
Some paragraph text here.

<!-- GOOD -->
## The Origins

Some paragraph text here.
```

---

## Sources Block

Always at the bottom, after a `---` rule, as an italic paragraph. No `###` header.

```md
---

*Sources: Publication Name, Publication Name, Author Name (Year).*

*Report compiled: Month YYYY.*
```

If sources are a numbered/linked list (academic style), keep the list but still place it after `---` with no header above it.

---

## Inline Formatting

- Bold (`**text**`) for proper nouns, key terms, and data points on first use in a section — use sparingly
- Italics (`*text*`) for publication names, foreign phrases, and emphasis
- No `#hashtag` style tags in the body (these belong in frontmatter `tags`)
- No promotional CTAs or Insertabot plugs in the body

---

## Tables

Use standard GFM tables. Column headers should be short. Align with pipes.

---

## Checklist for Incoming Articles

- [ ] Frontmatter: no blank lines between keys
- [ ] Frontmatter: tags as block list
- [ ] Filename: lowercase, hyphens only
- [ ] Body: no duplicate title/section header at top
- [ ] Body: all section labels are `##` or `###` headers
- [ ] Sources: after `---`, italic, no header
- [ ] No `#hashtag` lines in body
- [ ] No promotional CTAs
