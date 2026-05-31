import { defineConfig } from 'astro/config';
import mdx from '@astrojs/mdx';
import cloudflare from '@astrojs/cloudflare';

export default defineConfig({
  integrations: [mdx()],

  markdown: {
    shikiConfig: {
      theme: 'github-dark',
    },
  },

  site: 'https://mistykmedia.com',
  
  // Disable sessions to prevent auto-provisioning of KV namespace
  session: false,
  
  adapter: cloudflare()
});