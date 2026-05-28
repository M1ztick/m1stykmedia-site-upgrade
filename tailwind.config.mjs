/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}'],
  theme: {
    extend: {
      colors: {
        // Mistyk brand palette - muted, grounded
        'mistyk': {
          50: '#f8f7f5',
          100: '#efece8',
          200: '#ddd6cc',
          300: '#c4b8a8',
          400: '#a89580',
          500: '#8f7860',
          600: '#75614d',
          700: '#5f4f40',
          800: '#4f4136',
          900: '#433730',
        },
        // Section accents - subtle differentiation
        'dispatch': '#8b4513',    // Rust/documentary
        'archive': '#2d3748',     // Deep slate/music
        'workbench': '#4a5568',   // Steel/tools
        'current': '#553c2d',     // Earth/esoteric
      },
      fontFamily: {
        'display': ['Georgia', 'Cambria', 'serif'],
        'body': ['system-ui', '-apple-system', 'sans-serif'],
      },
    },
  },
  plugins: [require('@tailwindcss/typography')],
};