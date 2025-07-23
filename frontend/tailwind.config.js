import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        'saga-bg': '#0D0C1D',
        'saga-surface': '#16152C',
        'saga-primary': '#A78BFA',
        'saga-secondary': '#FBBF24',
        'saga-text-light': '#E0E0E0',
        'saga-text-dark': '#A0A0A0',
      },
      fontFamily: {
        'serif': ['var(--font-cormorant)', 'serif'],
        'sans': ['var(--font-inter)', 'sans-serif'],
      },
      backgroundImage: {
        'cosmic-gradient': 'radial-gradient(circle, rgba(22,21,44,1) 0%, rgba(13,12,29,1) 100%)',
      },
    },
  },
  plugins: [],
};
export default config;