import { defineConfig } from 'astro/config';
import mdx from '@astrojs/mdx';
import tailwind from '@astrojs/tailwind';

import cloudflare from "@astrojs/cloudflare";

export default defineConfig({
  integrations: [mdx(), tailwind()],

  markdown: {
    shikiConfig: {
      theme: 'github-dark',
    },
  },

  site: 'https://mistykmedia.com',
  adapter: cloudflare()
});