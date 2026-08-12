import typography from '@tailwindcss/typography';

/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // Fiber optic palette
        'coral': {
          DEFAULT: '#00D4FF',
          50: '#E0FAFF',
          100: '#B3F3FF',
          200: '#66E8FF',
          300: '#1ADCFF',
          400: '#00D4FF', // electric cyan — primary signal
          500: '#00AACF',
          600: '#007F9A',
          700: '#005568',
          800: '#002A35',
          900: '#001018',
        },
        'teal': {
          DEFAULT: '#7B2FFF',
          50: '#F0E8FF',
          100: '#D9C2FF',
          200: '#B385FF',
          300: '#9458FF',
          400: '#7B2FFF', // violet — secondary signal
          500: '#6318E0',
          600: '#4C0FB0',
          700: '#360A80',
          800: '#200550',
          900: '#0D0020',
        },
        // True black backgrounds
        'void': {
          DEFAULT: '#050508',
          50: '#0F1018',
          100: '#0A0B12',
          200: '#08090F',
          300: '#06070C',
          400: '#050508',
          500: '#030305',
          600: '#020203',
          700: '#010102',
          800: '#010101',
          900: '#000000',
        },
        // Cool white text
        'mist': {
          DEFAULT: '#E2EEFF',
          50: '#FFFFFF',
          100: '#F4F8FF',
          200: '#E2EEFF',
          300: '#C0D4F5',
          400: '#9DBAEB',
          500: '#7A9FE0',
          600: '#5785D6',
          700: '#3F6AB8',
          800: '#2C4F8A',
          900: '#1A335C',
        },
        // Section accents
        'dispatch': '#00D4FF',    // electric cyan — signal
        'journey': '#BF5FFF',     // bright violet — introspective
      },
      fontFamily: {
        'display': ['Inter', 'system-ui', 'sans-serif'],
        'body': ['Inter', 'system-ui', 'sans-serif'],
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'gradient-conic': 'conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))',
        'logo-gradient': 'linear-gradient(135deg, #00D4FF 0%, #7B2FFF 100%)',
      },
    },
  },
  plugins: [typography],
};
