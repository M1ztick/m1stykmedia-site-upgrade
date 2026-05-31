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
  
  // Explicitly disable sessions
  session: {
    driver: 'memory',
  },
  
  adapter: cloudflare({
    // Disable auto-provisioning of session KV binding
    sessionKVBindingName: false,
  })
});