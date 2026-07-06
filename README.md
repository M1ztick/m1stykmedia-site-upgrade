# Mistyk Media — Site Upgrade

A rebuild of Mistyk Media — the public platform for writer, developer, and recording artist 
Mistyk — migrating from WordPress to a static Astro architecture.

## Build

This is a blog-style setup with a focus on the **Dispatch** directory which features an
up-to-date collection of Mistyk's well-sourced and investigative essays and articles.
The rest is geared towards steering users towards Mistyk's other creative and 
technical pursuits via the appropriate links. 

| Section | Purpose | Color |
|---------|---------|-------|
| **The Dispatch** | Investigative writing, political analysis | Rust (#8b4513) |

## Tech Stack

- **Framework**: [Astro](https://astro.build/) (static-first)
- **Styling**: Tailwind CSS + custom brand palette
- **Content**: MDX for longform, YAML/JSON for structured data
- **Deployment**: Static hosting (Vercel/Netlify/Cloudflare Pages)

## Content Structure

```
src/
├── content/
│   ├── dispatch/    # Blog posts (MDX)
├── layouts/
│   └── Root.astro   # Base layout
├── pages/
│   ├── index.astro          # Crossroads (home)
│   ├── dispatch/index.astro # Blog listing
└── styles/
    └── global.css
```

## Design Notes

- **Muted palette**: Avoids the sterile white/gray/black of typical dev blogs
- **Subtle texture**: Noise overlay for analog warmth
- **Typography**: Georgia display, system UI for body—grounded, not decorative
- **Cross-pollination**: Footer surfaces latest from all sections

---

*Built in the pursuit of unity, to fearlessly uncover the truth.*
