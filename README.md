# Mistyk Media — Site Upgrade

A living archive rebuild. Four quadrants, one consciousness.

## Architecture

The site follows a **Crossroads** paradigm — home is a decision point, not a feed.

| Section | Purpose | Color |
|---------|---------|-------|
| **The Dispatch** | Investigative writing, political analysis | Rust (#8b4513) |
| **The Archive** | Original music, sonic experiments | Slate (#2d3748) |
| **The Workbench** | Developer projects, code tools | Steel (#4a5568) |
| **The Current** | AI/tech, consciousness, esoteric | Earth (#553c2d) |

## Tech Stack

- **Framework**: [Astro](https://astro.build/) (static-first)
- **Styling**: Tailwind CSS + custom brand palette
- **Content**: MDX for longform, YAML/JSON for structured data
- **Deployment**: Static hosting (Vercel/Netlify/Cloudflare Pages)

## Development

```bash
# Install
npm install

# Dev server
npm run dev

# Build
npm run build
```

## Content Structure

```
src/
├── content/
│   ├── dispatch/    # Blog posts (MDX)
│   ├── archive/     # Music releases (YAML)
│   └── workbench/   # Projects (YAML)
├── layouts/
│   └── Root.astro   # Base layout
├── pages/
│   ├── index.astro          # Crossroads (home)
│   ├── dispatch/index.astro # Blog listing
│   ├── archive/index.astro  # Music listing
│   ├── workbench/index.astro# Projects listing
│   └── current/index.astro  # Spiritual/AI listing
└── styles/
    └── global.css
```

## Design Notes

- **Muted palette**: Avoids the sterile white/gray/black of typical dev blogs
- **Subtle texture**: Noise overlay for analog warmth
- **Typography**: Georgia display, system UI for body—grounded, not decorative
- **Cross-pollination**: Footer surfaces latest from all sections

## Roadmap

- [ ] Real content migration from WordPress
- [ ] Music player integration
- [ ] Project detail pages
- [ ] Search functionality
- [ ] RSS feeds per section
- [ ] Dark mode toggle

---

*Built with intention, not placeholders.*