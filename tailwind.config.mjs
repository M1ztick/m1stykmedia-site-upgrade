import typography from '@tailwindcss/typography';

/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // Core brand colors from logo
        'coral': {
          DEFAULT: '#E85A5A',
          50: '#FCE8E8',
          100: '#F9D1D1',
          200: '#F3A3A3',
          300: '#ED7575',
          400: '#E85A5A', // Logo primary
          500: '#D43D3D',
          600: '#B03030',
          700: '#8A2626',
          800: '#641C1C',
          900: '#3E1212',
        },
        'teal': {
          DEFAULT: '#2EC4B6',
          50: '#E6F8F6',
          100: '#CFF1ED',
          200: '#9FE3DB',
          300: '#6FD5C9',
          400: '#2EC4B6', // Logo accent
          500: '#25A094',
          600: '#1C7C73',
          700: '#135851',
          800: '#0A3430',
          900: '#051A18',
        },
        // Deep navy backgrounds
        'void': {
          DEFAULT: '#0A0F1C',
          50: '#1A2133',
          100: '#151B2B',
          200: '#111625',
          300: '#0D121F',
          400: '#0A0F1C', // Logo background
          500: '#080C16',
          600: '#060910',
          700: '#04060B',
          800: '#020305',
          900: '#000000',
        },
        // Light variant for contrast
        'mist': {
          DEFAULT: '#E8ECF1',
          50: '#FFFFFF',
          100: '#F7F8FA',
          200: '#E8ECF1',
          300: '#C8D0DB',
          400: '#A8B4C4',
          500: '#8899AD',
          600: '#687E96',
          700: '#526375',
          800: '#3C4855',
          900: '#262E36',
        },
        // Section accents - derived from logo gradient
        'dispatch': '#E85A5A',    // Coral urgency
        'frequency': '#2EC4B6',   // Teal creativity  
        'workbench': '#8899AD',   // Steel/muted for tools
        'current': '#C75A9E',     // Purple blend between coral+teal
      },
      fontFamily: {
        'display': ['Inter', 'system-ui', 'sans-serif'],
        'body': ['Inter', 'system-ui', 'sans-serif'],
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'gradient-conic': 'conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))',
        'logo-gradient': 'linear-gradient(135deg, #E85A5A 0%, #2EC4B6 100%)',
      },
    },
  },
  plugins: [typography],
};
